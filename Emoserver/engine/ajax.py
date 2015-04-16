#!-*- coding=utf-8 -*-
from django.template import Template,Context
from django.shortcuts import render_to_response,RequestContext
from django.http import HttpResponse
from Emoserver.users.models import SiteUser
from models import Emotion,Tag,HotTags,HotEmos,ValidationCode
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from Emoserver.utils.decorators import admin_needed
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from short_message  import *
import operator
import json
from base64 import *
from datetime import *
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
			if tag_object.tag_bool_deleted==True:
				tag_object.tag_bool_deleted=False
				tag_object.save()
		except Tag.DoesNotExist:
			tag_object = None
	return tag_object

def lookuporinsert_tag(tag_name):
	tag_object = lookup_tag(tag_name)
	if not tag_object:
		tag_object = Tag()
		tag_object.tag_name = tag_name
		tag_object.tag_bool_deleted=False
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

'''
# {
#    "status":200,           
# //状态码可以为200,400.200表示保存成功 400表示失败
"emo_id":310,
"emo_author":"lzy";
"emo_id": 2032, //表情ID
"emo_detail": "/media/7/1.41904683968e%2B126JmFWDj3UNmMM.gif",//表情位置
"is_deleted": false,//是否已删除
"emo_popularity": 0,//热度
"emo_like": 0,//收藏数
"last_update":,
           
# //仅当状态码为200时返回该表情的ID，如果用户//标注的表情在数据库
# //中已存在，也会返回数据
# //表情的标签列表,标签的ＩＤ,标签的内容 
#    "tags":[
{"id": 1804, "name": "\u9ad8\u5174","tag_popularity":2},//表情的标签信息
{"id": 2221, "name": "happy","tag_popularity":3}
],                 
...
# }
'''

def get_latest_emo_info(emo):

	if emo:
		ret_data = dict()
		ret_data["status"] =  200
		ret_data["emo_id"] =  emo.emo_id
		ret_data["emo_author"]=get_username_by_id(emo.emo_id)
		ret_data["emo_detail"] = emo.emo_img
		ret_data["is_deleted"] = emo.emo_bool_deleted
		ret_data["emo_popularity"] = emo.emo_popularity
		ret_data["emo_like"] = emo.emo_like_num
		ret_data["last_update"]=emo.emo_last_update
		ret_data["tags"] = list()
		for tag in emo.emo_tag_list.all():
			tag_dict = dict()
			tag_dict["id"] = tag.tag_id
			tag_dict["name"] = tag.tag_name
			tag_dict["tag_popularity"]=tag.tag_popularity
			ret_data["tags"].append(tag_dict)
		return HttpResponse(json.dumps(ret_data))
	return ret_status(400)

def ret_status(status):
	return HttpResponse(json.dumps({"status":status}))

'''
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
'''
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





'''
# {
#    "status":200,           //状态码可以为200,400.200表示成功
# //400表示失败,失败不传回数据
#    "categories":{//热门表情的类别
#    "足球":[1,23,4], //表情的类别名，表情的ID编号列表
#    "篮球":[2,25,46], //表情的类别名，表情的ID编号列表
#    },
# }
'''
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

'''
# {
#    "status":200,           //状态码可以为200,400.200表示成功
# //400表示失败,失败不传回数据
#    "categories":[//热门表情的类别
#    "足球":[1,23,4], //表情的类别名，表情的ID编号列表
#    "篮球":[2,25,46], //表情的类别名，表情的ID编号列表
#    ],
# }
'''
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

def get_pk_tag(req):
	pk = req.get("pk",None)
	tag = req.get("tag",None)
	tag = tag.lstrip("#")
	return pk,tag



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
def AddHottag(request):
	if request.siteuser.is_superuser:
		if request.GET:
			pk,tag = get_pk_tag(request.GET)
			if pk and tag:
				hottag_object = None
				try:
					hottag_object = HotTags.objects.get(hottag_id=int(pk))	
				except HotTags.DoesNotExist:
					return ret_status(400)
				#can only add to his own emotion	
				tag_object = lookup_tag(tag)
				if tag_object:
					hottag_object.hottag_list.add(tag_object)
					hottag_object.save()
					return ret_status(200)
				else:
					return ret_status(400)
	return ret_status(400)

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

@admin_needed(login_url="/")
def RemoveHottag(request):
	#not allowed login in user
	if request.siteuser.is_superuser:
		if request.GET:
			pk,tag = get_pk_tag(request.GET)
			if pk and tag:
				hottag_object = None
				try:
					hottag_object = HotTags.objects.get(hottag_id=int(pk))	
				except HotTags.DoesNotExist:
					return ret_status(400)
				#can only add to his own emotion	
				tag_object = lookup_tag(tag)
				if tag_object:
					hottag_object.hottag_list.remove(tag_object)
					hottag_object.save()
					return ret_status(200)
				else:
					return ret_status(600)
	return ret_status(700)

'''
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
'''

def get_username_by_id(uid):
	try:
		user_object = SiteUser.objects.get(pk = uid)
	except:
		return ""
	return user_object.username

def get_user_by_id(uid):
	try:
		user_object = SiteUser.objects.get(pk = uid)
	# except User.DoesNotExist:
	except:
		return None
	return user_object

def get_user_by_username(uname):
	try:
		user_object = SiteUser.objects.get(username = uname )
	# except "User.DoesNotExist":
	except:
		return None
	return user_object
def get_tag_by_tagname(tagname):
	try:
		tag_object=Tag.objects.get(tag_name=tagname)
	# except Tag.DoesNotExist:
	except:
		return None
	return tag_object  


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

'''
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
'''
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
			if emo_object.emo_upload_user == request.siteuser or request.siteuser.is_superuser:
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
				if emo_object.emo_upload_user == request.siteuser or request.siteuser.is_superuser:
					tag_object = lookuporinsert_tag(tag)
					if tag_object:
						emo_object.emo_tag_list.add(tag_object)
						emo_object.emo_init_tag_list.add(tag_object)
						emo_object.save()

						tag_object.emo_list.add(emo_object)
						tag_object.save()
						return ret_status(200)
	return ret_status(400)




#search api 
'''  按作者搜索表情
会返回已经被删除的表情,通过is_deleted字段判断是否被删除
/app/search/author=xxx&sortby=1&page=1&count=50
//作者（base64编码），按照热度|时间排序（1为热度，2为时间），页码，每页返回的数目
返回的结果
{"status": 200,
"author":"1110310214",
"emos": [
{"emo_type": 2, //表情类型
"tags": [
{"id": 1804, "name": "\u9ad8\u5174","tag_popularity":2},//表情的标签信息
{"id": 2221, "name": "happy","tag_popularity":3}
],
"emo_id": 2032, //表情ID
"emo_detail": "/media/7/1.41904683968e%2B126JmFWDj3UNmMM.gif",//表情位置
"is_deleted": false,//是否已删除
"emo_popularity": 0,//热度
"emo_like": 0,//收藏数
"last_update":
},
......
],
"total_num":300,
"next_page":2 //下一页，如果为负值，则不存在下一页
}
'''
def search_emos_by_author(request,username,sortby="1",page="1",page_count="12"):
	#加入base64编码
	try:
		username=b64decode(username)
		page=int(page)
		page_count=int(page_count)
	except:
		return ret_status(400)

	cur_user=get_user_by_username(username)
	if cur_user==None:
		return ret_status(400)

	uid=cur_user.id
	ret_data={}

	if sortby=="1": #热度，热度最高的排在最前面
		all_emos=Emotion.objects.filter(emo_upload_user=uid,emo_bool_deleted=False).order_by("-emo_popularity")
	else:  #时间，最新更改的排在最前面
		all_emos=Emotion.objects.filter(emo_upload_user=uid,emo_bool_deleted=False).order_by("-emo_last_update")
	count=0
	if all_emos:
		try:
			emos_num=all_emos.count()
		except:
			return ret_status(400)
		ret_data = dict()
		ret_data["status"] = 200
		ret_data["total_num"]=emos_num
		ret_data["author"]=username
		ret_data["emos"]  = list()
		try:
			paginator = Paginator(all_emos, page_count) # Show 25 sub_emos per page
		except:
			return ret_status(400)
		try:
			sub_emos = paginator.page(page)
		except PageNotAnInteger:
			# If page is not an integer, deliver first page.
			sub_emos = paginator.page(1)
		except EmptyPage:
			# If page is out of range (e.g. 9999), deliver last page of results.
			sub_emos = paginator.page(paginator.num_pages)

		if page==paginator.num_pages:
			ret_data["next_page"]=(-1)
		elif page>=1 and page<paginator.num_pages:
			ret_data["next_page"]=page+1
		else:
			ret_status(400)

		for emo in sub_emos:
			tmpdict = dict()
			tmpdict["emo_type"] = emo.emo_type
			tmpdict["emo_id"] = emo.emo_id
			tmpdict["emo_detail"] = str(emo.emo_img)
			tmpdict["is_deleted"] = emo.emo_bool_deleted
			tmpdict["emo_popularity"] = emo.emo_popularity
			tmpdict["emo_like"] = emo.emo_like_num
			tmpdict["last_update"]=emo.emo_last_update
			tmpdict["tags"] = list()
			tags=emo.emo_tag_list.all()
			for tag in tags:
				tag_dict={}
				tag_dict["id"]=tag.tag_id
				tag_dict["name"]=tag.tag_name
				tag_dict["tag_popularity"]=tag.tag_popularity
				tmpdict["tags"].append(tag_dict)
			ret_data["emos"].append(tmpdict)

		return HttpResponse(json.dumps(ret_data))
	return ret_status(400)

'''按标签搜索表情
/app/search/tag=xxx&sortby=1&page=1&count=50
//标签（base64编码），按照热度|时间排序（1为热度，2为时间），页码，每页返回的数目
{"status": 200,
"tag":{"id": 2221, "name": "happy","popularity":2,"is_deleted":false,"last_update":1427770195168},//搜索的标签信息
"emos": [
{"emo_type": 2, //表情类型
"emo_id": 2032, //表情ID
"emo_detail": "/media/7/1.41904683968e%2B126JmFWDj3UNmMM.gif",//表情位置
"emo_author": "nono_1984@163.com",//作者信息
"is_deleted": false,//是否已删除
"emo_popularity": 0,//热度
"emo_like": 0,//收藏数
"last_update":1427770195168 //最后更新时间戳
},
...
],
"total_num":300,//总数
"next_page":2//下一页，如果为负值，则不存在下一页
}
'''
def search_emos_by_tag(request,tag_name,sortby="1",page="1",page_count="12"):
	#加入base64编码
	try:
		tag_name=b64decode(tag_name)
		page=int(page)
		page_count=int(page_count)
	except:
		return ret_status(400)
	cur_tag=get_tag_by_tagname(tag_name)
	if cur_tag==None:
		return ret_status(400)
	tag_id=cur_tag.tag_id
	ret_data={}

	if sortby=="1": #热度，热度最高的排最前
		all_emos=cur_tag.emo_list.filter(emo_bool_deleted=False).order_by("-emo_popularity")
	else:  #时间，最新更新的排最前
		all_emos=cur_tag.emo_list.filter(emo_bool_deleted=False).order_by("-emo_last_update")
	count=0

	if all_emos:
		try:
			emos_num=all_emos.count()
		except:
			return ret_status(400)
		ret_data = dict()
		ret_data["status"] = 200
		ret_data["total_num"]=emos_num
		ret_data["emos"]  = list()
		ret_data["tag"]={}		
		ret_data["tag"]["id"]=cur_tag.tag_id
		ret_data["tag"]["name"]=cur_tag.tag_name
		ret_data["tag"]["popularity"]=cur_tag.tag_popularity
		ret_data["tag"]["is_deleted"]=cur_tag.tag_bool_deleted
		ret_data["tag"]["last_update"]=cur_tag.tag_last_update
		try:
			paginator = Paginator(all_emos, page_count) # Show 25 sub_emos per page
		except:
			return ret_status(400)
		try:
			sub_emos = paginator.page(page)
		except PageNotAnInteger:
			# If page is not an integer, deliver first page.
			sub_emos = paginator.page(1)
		except EmptyPage:
			# If page is out of range (e.g. 9999), deliver last page of results.
			sub_emos = paginator.page(paginator.num_pages)

		if page==paginator.num_pages:
			ret_data["next_page"]=(-1)
		elif page>=1 and page<paginator.num_pages:
			ret_data["next_page"]=page+1
		else:
			ret_status(400)

		for emo in sub_emos:
			tmpdict = dict()
			tmpdict["author"]=get_username_by_id(emo.emo_id)
			tmpdict["emo_type"] = emo.emo_type
			tmpdict["emo_id"] = emo.emo_id
			tmpdict["emo_detail"] = str(emo.emo_img)
			tmpdict["is_deleted"] = emo.emo_bool_deleted
			tmpdict["emo_popularity"] = emo.emo_popularity
			tmpdict["emo_like"] = emo.emo_like_num
			tmpdict["last_update"]=emo.emo_last_update
			ret_data["emos"].append(tmpdict)
		return HttpResponse(json.dumps(ret_data))
	return ret_status(400)

def first_page_data(request,sortby="1",page="1",page_count="12"):
	try:
		page=int(page)
		page_count=int(page_count)
	except:
		return ret_status(400)
	ret_data={}

	if sortby=="1": #热度，热度最高的排在最前面
		all_emos=Emotion.objects.filter(emo_bool_deleted=False).order_by("-emo_popularity")
	else:  #时间，最新更改的排在最前面
		all_emos=Emotion.objects.filter(emo_bool_deleted=False).order_by("-emo_last_update")

	if all_emos:
		try:
			emos_num=all_emos.count()
		except:
			return ret_status(400)
		ret_data = dict()
		ret_data["status"] = 200
		ret_data["total_num"]=emos_num
		ret_data["emos"]  = list()
		try:
			paginator = Paginator(all_emos, page_count) # Show 25 sub_emos per page
		except:
			return ret_status(400)
		try:
			sub_emos = paginator.page(page)
		except PageNotAnInteger:
			# If page is not an integer, deliver first page.
			sub_emos = paginator.page(1)
		except EmptyPage:
			# If page is out of range (e.g. 9999), deliver last page of results.
			sub_emos = paginator.page(paginator.num_pages)

		if page==paginator.num_pages:
			ret_data["next_page"]=(-1)
		elif page>=1 and page<paginator.num_pages:
			ret_data["next_page"]=page+1
		else:
			ret_status(400)

		for emo in sub_emos:
			tmpdict = dict()
			tmpdict["emo_type"] = emo.emo_type
			tmpdict["emo_id"] = emo.emo_id
			tmpdict["author"] = str(emo.emo_upload_user)
			tmpdict["emo_detail"] = str(emo.emo_img)
			tmpdict["is_deleted"] = emo.emo_bool_deleted
			tmpdict["emo_popularity"] = emo.emo_popularity
			tmpdict["emo_like"] = emo.emo_like_num
			tmpdict["last_update"]=emo.emo_last_update
			tmpdict["tags"] = list()
			tags=emo.emo_tag_list.all()
			for tag in tags:
				tag_dict={}
				tag_dict["id"]=tag.tag_id
				tag_dict["name"]=tag.tag_name
				tag_dict["tag_popularity"]=tag.tag_popularity
				tmpdict["tags"].append(tag_dict)
			ret_data["emos"].append(tmpdict)

		return HttpResponse(json.dumps(ret_data))
	return ret_status(400)

def get_emo_html(request,emoid):
	try:
		emo_object=Emotion.objects.get(emo_id=int(emoid))
	except:
		return ret_status(400)

	data_dictionary={}
	data_dictionary["emo_detail"]=emo_object.emo_img
	try:
		return render_to_response("get_emo_html.html",data_dictionary,context_instance=RequestContext(request))
	except:
		return ret_status(400)



'''
{
	"emo_id":"1",
	"share_type":"1",
}
'''
@csrf_exempt
def save_share_info(request):
	if request.POST:
		try:
			share_data = json.loads(request.body)
		except:
			return ret_status(400)
		emo_id = share_data.get("emo_id",None)		
		share_type = share_data.get("share_type",None)		
		if not emo_id:
			return ret_status(400)
		if not share_type:
			return ret_status(400)
		emo_object = None
		try:
			try:
				emo_object = Emotion.objects.get(emo_id=int(emo_id))
			except:
				return ret_status(400)
			if emo_object:
				emo_object.emo_popularity+=1
				if share_type=="1":
					emo_object.weixin_send_num+=1
				elif share_type=="2":
					emo_object.weixin_share_num+=1
				elif share_type=="3":
					emo_object.weibo_share_num+=1
				else:
					emo_object.emo_like_num+=1				
				emo_object.save()
				return ret_status(200)
			else:
				return ret_status(400)
		except:
			return ret_status(400)
	return ret_status(400)

def get_and_save_vali_code(request,mobile=None):
	if not mobile:
		return ret_status(400)
	try:
		vali_code_object=ValidationCode()
		cur_datetime=datetime.now()
		vali_code_object.vali_code=str(cur_datetime.microsecond)
		expire_time= cur_datetime+timedelta(2)
		vali_code_object.expire_time=expire_time
		vali_code_object.save()	
	except:
		return ret_status(400)
	try:
		ret_data={}
		ret_data["status"] =  200
		ret_data["vali_code"]=vali_code_object.vali_code
		num=send_short_message(mobile,vali_code_object.vali_code)
		if num==1:
			return HttpResponse(json.dumps(ret_data))
		else:
			return ret_status(400)
	except:
		return ret_status(400)

#验证用户发来的验证码是否在数据库中，如果在的话是否过期
def verify_vali_code(request,vali_code=None):
	if not vali_code:
		return ret_status(400)
	try:
		vali_code_object=ValidationCode.objects.get(vali_code=vali_code)
	except:
		return ret_status(400)
	try:
		expire_time=vali_code_object.expire_time
		# print expire_time
	except:
		return ret_status(400)
	cur_time=datetime.now()
	# print cur_time
	expire_time = datetime.strptime(str(expire_time).rstrip("+00:00"), "%Y-%m-%d %H:%M:%S")	
	if expire_time<cur_time:
		return ret_status(400)
	return ret_status(200)

