#!-*- coding=utf-8 -*-
from django.template import Template,Context
from django.shortcuts import render_to_response,RequestContext
from django.http import HttpResponse
from Emoserver.users.models import SiteUser
from models import Emotion,Tag,HotTags,HotEmos
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from Emoserver.utils.decorators import admin_needed
import operator
import json

EMO_TEXT = 1 
EMO_MOTION = 2

ANOYMOUS = 1
MAX_EMOTION_LEN = 255

#if the tag exist return it
#if not then inset and return it

def lookup_tag(tag_name):
	tag_name = tag_name.strip()
	tag_object = None
	if tag_name:
		try:
			tag_object = Tag.objects.get(tag_name=tag_name)
		except Tag.DoesNotExist:
			tag_object = None
	return tag_object

def lookuporinsert_tag(tag_name):
	tag_object = lookup_tag(tag_name)
	if not tag_object:
		tag_object = Tag()
		tag_object.tag_name = tag_name
		tag_object.save()
	return tag_object


#if the emotion exist return it
#if not inset and return it
def lookuporinsert_emo(emotion):
	emotion = emotion.strip()
	emo_object = None
	if emotion:
		try:
			emo_object = Emotion.objects.get(emo_content=emotion)
		except Emotion.DoesNotExist:
			emo_object = None
		if not emo_object:
			#create emo object
			emo_object = Emotion()

			emo_object.emo_content = emotion
			emo_object.emo_upload_user = get_user_by_id(ANOYMOUS)
			emo_object.emo_type = EMO_TEXT

			emo_object.save()
		return emo_object
	return None

# {
#    "status":200,           
# //状态码可以为200,400.200表示保存成功 400表示失败
#    "emo_id":310,           
# //仅当状态码为200时返回该表情的ID，如果用户//标注的表情在数据库
# //中已存在，也会返回数据
# //表情的标签列表,标签的ＩＤ,标签的内容 
#    "tags":{                  
# 	   1:"soccer",      
# 	   2:"football"
# 	}
# }


def get_latest_emo_info(Emotion_Object):

	if Emotion_Object:
		ret_data = dict()
		ret_data["status"] =  200
		ret_data["emo_id"] =  Emotion_Object.emo_id
		
		#get the tags
		ret_data["tags"] = list()
		for tag in Emotion_Object.emo_tag_list.all():
			tag_dict = dict()
			tag_dict["id"] = tag.tag_id
			tag_dict["name"] = tag.tag_name
			ret_data["tags"].append(tag_dict)

		return HttpResponse(json.dumps(ret_data))
	return ret_status(400)

def ret_status(status):
	return HttpResponse(json.dumps({"status":status}))


#app side user annotate the emotion
#the server sider save the annotation and 
#return the latest tags the app side	
# data format that posted by app
# {
#    "emo_type":1,           //表情的类型可以为
#                              // 1：文字表情（可以为文字，icon或者文字icon
# //组合） 2：动画表情
#    "emo_id":310,           //如果为动画表情，则存在该字段,指明表情的ID
#    "emo_detail":"看星星",  //如果为文字表情则存在该字段，为表情的内容
                         
#    "tags":[            //给表情打的标签列表
# 	   "soccer",     //可以同时打多个标签
# 	   "football"
# 	]
# }
@csrf_exempt
def annoate_emotion(request):
	if request.POST:
		tag_data = json.loads(request.body)
		print tag_data
		emo_type = tag_data.get("emo_type",None)
		
		emo_object = None
		try:
			if emo_type != None:
				emo_type = int(emo_type)
				#if it is text emotion, find it or save it
				if emo_type == EMO_TEXT:
					emo_detail = tag_data.get("emo_detail",None)
					if emo_detail and len(emo_detail) <= MAX_EMOTION_LEN:
						emo_object = lookuporinsert_emo(emo_detail)

				#motions must have an ID
				elif emo_type == EMO_MOTION:
					emo_id = tag_data.get("emo_id",None)
					if emo_id:
						try:
							emo_object = Emotion.objects.get(emo_id=int(emo_id))
						except Emotion.DoesNotExist:
							return ret_status(400)

				#save the new tag
				if emo_object:
					for tag in tag_data.get("tags",[]):
						tag_object = lookuporinsert_tag(tag)
						if tag_object:
							emo_object.emo_tag_list.add(tag_object)
							emo_object.emo_init_tag_list.add(tag_object)
							#save the emotion to the tag as well
							tag_object.emo_list.add(emo_object)
							tag_object.save()
					emo_object.save()
					return get_latest_emo_info(emo_object)
		except:
			return ret_status(400)
	return ret_status(400)

# {
#    "status":200,           //状态码可以为200,400.200表示成功
# //400表示失败,失败不传回数据
#    "categories":{//热门表情的类别
#    "足球":[1,23,4], //表情的类别名，表情的ID编号列表
#    "篮球":[2,25,46], //表情的类别名，表情的ID编号列表
#    },
# }
def get_hottags(request):
	#if request.is_ajax():
	all_hottags = HotTags.objects.all()

	if all_hottags:
		ret_data = dict()

		ret_data["status"] = 200
		ret_data["categories"]  = list()
		for hottag in all_hottags:
			tag_dict = dict()
			tag_dict["name"] = hottag.hottag_category
			tag_dict["taglist"] = [tag.tag_id for tag in hottag.hottag_list.all()]
			
			ret_data["categories"].append(tag_dict)
		return HttpResponse(json.dumps(ret_data))
	return ret_status(400)


# {
#    "status":200,           //状态码可以为200,400.200表示成功
# //400表示失败,失败不传回数据
#    "categories":[//热门表情的类别
#    "足球":[1,23,4], //表情的类别名，表情的ID编号列表
#    "篮球":[2,25,46], //表情的类别名，表情的ID编号列表
#    ],
# }

def get_hotemos(request):
	#if request.is_ajax():
	all_hotemos = HotEmos.objects.all()

	if all_hotemos:
		ret_data = dict()

		ret_data["status"] = 200
		ret_data["categories"]  = list()
		for hotemo in all_hotemos:
			tmpdict = dict()
			tmpdict["name"] = hotemo.hotemo_category
			tmpdict["emos"] = [emo.emo_id for emo in hotemo.hotemo_list.all()]
			#ret_data["categories"][hotemo.hotemo_category] = 
			ret_data["categories"].append(tmpdict)
		return HttpResponse(json.dumps(ret_data))
	return ret_status(400)



@admin_needed(login_url="/")
def CreateHotemo(request):
	if request.POST:
		tags = request.POST.get("emo_tag",[])
		emo_type = request.POST.get("emo_type",2)
		cate = request.POST.get("cate","")
		if not tags and not cate:
			return HttpResponse(json.dumps({"ok":False,"msg":"标签不能为空~~"}))
		if HotEmos.objects.filter(hotemo_category=cate):
			return HttpResponse(json.dumps({"ok":False,"msg":"相同的类别已经存在了哦~~"}))
		if tags:
			
			tag_name_list = [tag for tag in tags.split(',')]
			emo_object_list = Emotion.objects.filter(emo_type=emo_type).filter(reduce(operator.and_, \
				(Q(emo_tag_list__tag_name__contains=x) for x in tag_name_list)))
			if emo_object_list:
				
				hotemos = HotEmos()
				hotemos.hotemo_category = cate
				hotemos.save()
				for emo in emo_object_list:
					hotemos.hotemo_list.add(emo)
				hotemos.save()

				return HttpResponse(json.dumps({"ok":True}))
			else:
				return HttpResponse(json.dumps({"ok":False,"msg":"没有符合要求的表情哦~~"}))
		else:
			HttpResponse(json.dumps({"ok":False,"msg":"没有收到合法的数据"}))
			
	return HttpResponse(json.dumps({"ok":False,"msg":"请求方法错误"}))


@admin_needed(login_url="/")
def CreateHottag(request):
	if request.POST:
		cate = request.POST.get("cate",None)		
		tags = request.POST.get("tags",None)
		if not cate or not tags:
			return HttpResponse(json.dumps({"ok":False,"msg":"标签不能为空~~"}))

		if HotTags.objects.filter(hottag_category=cate):
			return HttpResponse(json.dumps({"ok":False,"msg":"相同的类别已经存在了哦~~"}))
		
		tag_list_raw = [ lookup_tag(tag) for tag in tags.split(',')]
		tag_list = [ tag_object for tag_object in tag_list_raw if tag_object]
		if not tag_list:
			return HttpResponse(json.dumps({"ok":False,"msg":"数据库不存在添加的标签"}))
		
		hottags = HotTags()
		hottags.hottag_category = cate
		hottags.save()

		for tag_object in tag_list:
			if tag_object:
				hottags.hottag_list.add(tag_object)
		hottags.save()
		return HttpResponse(json.dumps({"ok":True}))
	else:
		return HttpResponse(json.dumps({"ok":False,"msg":"请求方法错误"}))

@admin_needed(login_url="/")
def DeleteHotemo(request):
	hotemo_id = request.GET.get("id",None) 
	if hotemo_id:
		try:
			HotEmos.objects.get(hotemo_id=hotemo_id).delete()
			return HttpResponse(json.dumps({"ok":True}))
		except:
			return HttpResponse(json.dumps({"ok":False,"msg":"删除失败"}))
	else:
		return HttpResponse(json.dumps({"ok":False,"msg":"该热门表情组不存在"}))

@admin_needed(login_url="/")
def DeleteHottag(request):
	hottag_id = request.GET.get("id",None) 
	if hottag_id:
		try:
			HotTags.objects.get(hottag_id=hottag_id).delete()
			return HttpResponse(json.dumps({"ok":True}))
		except:
			return HttpResponse(json.dumps({"ok":False,"msg":"删除失败"}))
	else:
		return HttpResponse(json.dumps({"ok":False,"msg":"该热门标签组不存在"}))


#/app/updatetemap?_t=20140201222

# {
#    "status":200,           //状态码可以为200,400.200表示成功
# //400表示失败,失败不传回数据
#    "emos"[{   //表情信息,是一个列表
# 	   "emo_id":320, //320为表情的ID
# 	   "emo_type":1, //表情的类型
	   
# 	   "emo_detail": //如果表情的类型为图片，则为服务端的请求地址，如//"/static/emo/320.gif"
# 	//如果为文字，则为该表情的具体内容
# 	   "emo_author":"little_star",//该表情的作者
# 	   "emo_popularity":100,    //该表情的流行度
# 	   "emo_like":50,           //收藏该表情的人数
# 	   "tags":{                  //给表情打的标签列表
# 		   1:"soccer",     
# 		   2:"football"
# 	    }
# 	   }
#    ],
#    "next_cusor":20140405     //下次请求的timestamp

# }


def get_username_by_id(uid):
	try:
		user_object = SiteUser.objects.get(pk = uid)
	except User.DoesNotExist:
		return ""
	return user_object.username

def get_user_by_id(uid):
	try:
		user_object = SiteUser.objects.get(pk = uid)
	except User.DoesNotExist:
		return None
	return user_object


#update emo-tag  map
def updateetmap(request,cursor):
	cursor = long(cursor)
	emo_tag_map = Emotion.objects.filter(emo_last_update__gt=cursor).order_by("emo_last_update")[:2000]
	emo_tag_count = emo_tag_map.count()
	if emo_tag_count <= 0:
		return ret_status(400)

	next_cusor = emo_tag_map[emo_tag_count-1]

	if emo_tag_map:
		ret_data = dict()
		ret_data["status"] = 200
		ret_data["next_cusor"] = next_cusor.emo_last_update
					
		ret_data["emos"] = list()

		for emo in emo_tag_map:
			tmp_dict = dict()

			tmp_dict["emo_id"] = emo.emo_id
			tmp_dict["emo_type"] = emo.emo_type

			if tmp_dict["emo_type"] == EMO_TEXT:
				tmp_dict["emo_detail"] = emo.emo_content
			elif tmp_dict["emo_type"] == EMO_MOTION:
				tmp_dict["emo_detail"] = emo.emo_img.url
			#username = get_username_by_id(emo.emo_upload_uid)

			
			tmp_dict["emo_author"] = emo.emo_upload_user.username
			tmp_dict["emo_popularity"] = emo.emo_popularity
			tmp_dict["emo_like"] = emo.emo_like_num
			tmp_dict["is_deleted"] = emo.emo_bool_deleted		
			tmp_dict["tags"] = list()

			for tag in emo.emo_tag_list.all():
				tag_dict = dict()
				tag_dict["id"] = tag.tag_id
				tag_dict["name"] = tag.tag_name
	
				tmp_dict["tags"].append(tag_dict)
			
			ret_data["emos"].append(tmp_dict)

		return HttpResponse(json.dumps(ret_data))
	return ret_status(400)


# {
#    "status":200,           //状态码可以为200,400.200表示成功
# //400表示失败,失败不传回数据
#    "tags"[ { //标签信息
# 	   "tag_id":320, //320为标签的ID
# 	   "tag_name":"世界杯", //标签的名称 
# 	   "tag_popularity":100,    //该标签的流行度
# 	   "emos":[                  //与该标签对应的表情ID号
# 		   1,2,3,4
# 	    ]
# 	   }
#	}
#    ],
#    "next_cusor":20140405     //下次请求的timestamp
# }

#update tag-emo map
def updatetemap(request,cursor):

	cursor = long(cursor)
	tag_emo_map = Tag.objects.filter(tag_last_update__gt=cursor).order_by("tag_last_update")[:2000]
	tag_emo_count = tag_emo_map.count()
	if tag_emo_count <= 0:
		return ret_status(400)
	next_cusor = tag_emo_map[tag_emo_count-1]

	if tag_emo_map:
		ret_data = dict()
		ret_data["status"] = 200
		ret_data["next_cusor"] = next_cusor.tag_last_update
		ret_data["tags"] = list()

		for tag in tag_emo_map:
			tmp_dict = dict()
			tmp_dict["tag_id"] = tag.tag_id
			tmp_dict["tag_name"] = tag.tag_name
			tmp_dict["tag_popularity"] = tag.tag_popularity
			tmp_dict["is_deleted"] = tag.tag_bool_deleted
			if not tmp_dict["is_deleted"]:	
				tmp_dict["emos"] = [emo.emo_id for emo in tag.emo_list.all()]
			if tag.emo_list.count() > 0 :
				tmp_dict["cover"] = tag.emo_list.all()[0].emo_content
			
			ret_data["tags"].append(tmp_dict)

		return HttpResponse(json.dumps(ret_data))

	return ret_status(400)


def get_pk_tag(req):
	pk = req.get("pk",None)
	tag = req.get("tag",None)
	tag = tag.lstrip("#")
	return pk,tag


'''

 add or remove tag from management screen

'''
def removetag(request):
	#not allowed login in user
	if request.siteuser:
		if request.GET:
			pk,tag = get_pk_tag(request.GET)
			emo_object = None

			try:
				emo_object = Emotion.objects.get(emo_id=pk)	
			except Emotion.DoesNotExist:
				return ret_status(400)
			#can only delete his own emotion tag	
			if emo_object.emo_upload_user == request.siteuser:
				tag_object = lookup_tag(tag)
				if tag_object:
					emo_object.emo_init_tag_list.remove(tag_object)
					emo_object.emo_tag_list.remove(tag_object)
					emo_object.save()
					tag_object.emo_list.remove(emo_object)
					if not tag_object.emo_list.count():
						tag_object.tag_bool_deleted = True
					tag_object.save()
					return ret_status(200)
	return ret_status(400)

def addtag(request):
	#not allowed login in user
	if request.siteuser:
		if request.GET:
			pk,tag = get_pk_tag(request.GET)
			if pk and tag:
				emo_object = None
				try:
					emo_object = Emotion.objects.get(emo_id=int(pk))	
				except Emotion.DoesNotExist:
					return ret_status(400)
				#can only add to his own emotion	
				if emo_object.emo_upload_user == request.siteuser:
					tag_object = lookuporinsert_tag(tag)
					if tag_object:
						emo_object.emo_tag_list.add(tag_object)
						emo_object.emo_init_tag_list.add(tag_object)
						emo_object.save()

						tag_object.emo_list.add(emo_object)
						tag_object.save()
						return ret_status(200)
	return ret_status(400)


def search_emos_by_author(request):
	return ret_status(400)


def search_emos_by_tag(request):
	return ret_status(400)
