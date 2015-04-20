#!/usr/bin/python
#-*- encoding=utf-8 -*-

from django.template import Template,Context
from django.shortcuts import render_to_response,RequestContext
from django.http import HttpResponse,HttpResponseRedirect
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import authenticate,login,logout
from Emoserver.utils.decorators import login_needed
from django.views.generic import CreateView, DeleteView, ListView
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse
from django.db.models import Count
from .models import Emotion,Tag,HotTags,HotEmos
from Emoserver.users.models import SiteUser,ValidationCode
from .response import JSONResponse, response_mimetype
from .serialize import serialize
from .forms import UploadForm,registerForm
from .ajax import *
from Emoserver.utils.decorators import admin_needed
import json
from short_message  import *
from base64 import *
import re 
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

EMO_TEXT = 1 
EMO_MOTION = 2

def index(request):
    context = RequestContext(request)
    if request.siteuser:
        if request.siteuser.is_superuser:
            return HttpResponseRedirect("list/hotemo")
        return HttpResponseRedirect("upload/new")
    return render_to_response("base_login.html",context)

def test(request):
    ret_data={}
    username=request.GET.get("author",None)
    if username==None:
        return ret_status(400)
    else:
        user_object=get_user_by_username(username)
        ret_data["status"]=200
        ret_data["user"]=user_object.username
        ret_data["requestuser"]=request.siteuser.username
        ret_data["flag"]=request.siteuser==user_object
        return HttpResponse(json.dumps(ret_data))

@admin_needed(login_url="/")
def sysinfo(request):
    ret_data={}
    ret_data["pic_num"] = Emotion.objects.exclude(emo_bool_deleted=True).count()
    ret_data["user_num"] = SiteUser.objects.exclude(is_active=False).count()
    #除去已经删除的标签
    ret_data["tag_num"] = Tag.objects.filter(tag_bool_deleted=False).count()
    # tag_num = Tag.objects.count()
    ret_data["user_info"]=[]
    user_list=SiteUser.objects.all()
    for user in user_list:
        tmp={}
        tmp["num"]=Emotion.objects.filter(emo_upload_user=user.id,emo_bool_deleted=False).count()
        tmp["username"]=user.username
        ret_data["user_info"].append(tmp)
    return render_to_response("sys_info.html",ret_data,RequestContext(request))
    # return HttpResponse(json.dumps(ret_data))
# def register(request):
#     return render_to_response("register.html")

# @csrf_protect
# def mylogin(request):
#     context = RequestContext(request)

#     if request.method == "POST":
#         username = request.POST.get("username","")
#         password = request.POST.get("password","")


#         user = authenticate(username=username,password=password)
#         if user:
#             if user.is_active:
#                 login(request,user)
#                 request.session.set_expiry(0)
#                 return HttpResponseRedirect("/upload/new")
#         #return render_to_response("fileupload/picture_form.html")
#         else:
#             return render_to_response("base_login.html",\
#         {"err_msg":u'用户名或密码错误',"username":username,"password":password},context)


# @login_needed(login_url='/')
# def loginout(request):
# 	logout(request)
# 	return HttpResponseRedirect("/")




    # emo_id = models.AutoField(primary_key=True)
    # emo_type = models.PositiveSmallIntegerField(choices=EMO_TYPE_CHOICES)

    # #store the image content
    # emo_img = models.ImageField(upload_to=get_emoimg_url,blank=True)
    # emo_content = models.TextField(blank=True)

    # emo_upload_user = models.ForeignKey(UserProfile)
    # emo_tag_list = models.ManyToManyField(Tag,related_name="tag")
    # emo_init_tag_list = models.ManyToManyField(Tag,related_name="init_tag")

    # emo_popularity = models.IntegerField(default=0)
    # emo_like_num = models.IntegerField(default=0)
    # emo_last_update = models.BigIntegerField()

class UserCreateView(CreateView):
    pass
    # model = SiteUser
    # form_class = registerForm
    # template_name = "base_login.html"
    

    # def form_valid(self,form):
    #     # self.object = form.save(commit=False)
    #     # print form.cleaned_data
    #     username = form.cleaned_data["username"]
    #     password = form.cleaned_data["password"]
    #     email = form.cleaned_data["email"]
    #     self.object = User.objects.create_user(username,\
    #         password=password,email=email)
    #     self.object.is_staff = False
    #     self.object.is_active = True
    #     self.object.is_superuser = False
    #     self.object.save()
    #     return HttpResponseRedirect("/")

    # def form_invalid(self,form):

    #     #return render_to_response("base_login.html",{"register_errors":form.errors})
    #     data = json.dumps(form.errors)
    #     return HttpResponse(content=data, status=400, content_type='application/json')

class PictureCreateView(CreateView):

    model = Emotion
    form_class = UploadForm
    template_name = "upload_new.html"
    tag_pattern = re.compile("^[a-zA-Z\d\u0391-\uFFE5]{1,10}$")


    @method_decorator(login_needed(login_url="/"))
    def dispatch(self, *args, **kwargs):
        return super(PictureCreateView, self).dispatch(*args, **kwargs)


    def form_valid(self, form):

        self.object = form.save(commit=False)

        self.object.emo_type = EMO_MOTION
        self.object.emo_upload_user = self.request.siteuser
        self.object.emo_bool_deleted = False
        self.object.save()

        for tag in form.cleaned_data.get("tags","").split():
            # tag = tag.decode("utf-8")
            # if not self.tag_pattern.match(tag):
            #     continue
            tag_object = lookuporinsert_tag(tag)
            if tag_object:
                #add to inititial taglist and tag_list
                #emo object
                self.object.emo_init_tag_list.add(tag_object)
                self.object.emo_tag_list.add(tag_object)
                #save the emotion to tag as well
                tag_object.emo_init_list.add(self.object)
                tag_object.save()

        self.object.save()

        files = [serialize(self.object)]
        data = {'files': files}
        response = JSONResponse(data, mimetype=response_mimetype(self.request))
        response['Content-Disposition'] = 'inline; filename=files.json'
        return response

    def form_invalid(self, form):
        data = json.dumps(form.errors)
        return HttpResponse(content=data, status=400, content_type='application/json')


class CreateemoForOthers(CreateView):
    model = Emotion
    form_class = UploadForm
    template_name = "upload_new_for_others.html"
    tag_pattern = re.compile("^[a-zA-Z\d\u0391-\uFFE5]{1,10}$")
    @method_decorator(admin_needed(login_url="/"))
    def dispatch(self, *args, **kwargs):
        username = self.kwargs.get("author",None)
        return super(CreateemoForOthers, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        username = self.kwargs.get("author",None)
        print username
        user_object=get_user_by_username(username)
        self.object = form.save(commit=False)
        self.object.emo_type = EMO_MOTION
        self.object.emo_upload_user = user_object
        self.object.emo_bool_deleted = False
        self.object.save()

        for tag in form.cleaned_data.get("tags","").split():
            # tag = tag.decode("utf-8")
            # if not self.tag_pattern.match(tag):
            #     continue
            tag_object = lookuporinsert_tag(tag)
            if tag_object:
                #add to inititial taglist and tag_list
                #emo object
                self.object.emo_init_tag_list.add(tag_object)
                self.object.emo_tag_list.add(tag_object)
                #save the emotion to tag as well
                tag_object.emo_init_list.add(self.object)
                tag_object.save()

        self.object.save()

        files = [serialize(self.object)]
        data = {'files': files}
        response = JSONResponse(data, mimetype=response_mimetype(self.request))
        response['Content-Disposition'] = 'inline; filename=files.json'
        return response
    def form_invalid(self, form):
        data = json.dumps(form.errors)
        return HttpResponse(content=data, status=400, content_type='application/json')


class PictureDeleteView(DeleteView):
    model = Emotion
    #success_url = reverse("upload_view")
    #model = Emotion

    @method_decorator(login_needed(login_url="/"))
    def dispatch(self, *args, **kwargs):
        return super(PictureDeleteView, self).dispatch(*args, **kwargs)

    # def get_success_url(self):
    #     return reverse("upload-view",)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        #do not delete the picture
        self.object.emo_bool_deleted = True

        #delete the tag emotion map
        for tag_object in self.object.emo_init_tag_list.all():
            tag_object.emo_init_list.remove(self.object)
            if not tag_object.emo_init_list.count():
                tag_object.tag_bool_deleted = True
            tag_object.save()

        for tag_object in self.object.emo_tag_list.all():
            tag_object.emo_list.remove(self.object)
            if not tag_object.emo_list.count():
                tag_object.tag_bool_deleted = True
            tag_object.save()

        self.object.save()
        # response = JSONResponse(True, mimetype=response_mimetype(request))
        # response['Content-Disposition'] = 'inline; filename=files.json'
        return HttpResponseRedirect("/search/view")



@login_needed(login_url="/")
def PictureListView(request,page=1,page_count=2):
    page=request.GET.get('page',None)
    if page==None:
        page=1
    page=int(page)
    object_list=Emotion.objects.filter(emo_upload_user=request.siteuser,emo_bool_deleted=False)\
                .exclude(emo_img__isnull=True).order_by("-emo_popularity")
    try:
        paginator = Paginator(object_list, page_count) # Show 25 sub_emos per page
    except:
        return ret_status(400)
    try:
        sub_emos = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        sub_emos = paginator.page(page)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        sub_emos = paginator.page(paginator.num_pages)
    return render_to_response("upload_view.html",locals(),context_instance=RequestContext(request))



class UserWorkListView(ListView):
    #model = Emotion
    #context_object_name = "emotion_list" 
    template_name = "list_work_view.html"
    #paginate_by = 100

    def get_queryset(self):
        return Emotion.objects.filter(emo_upload_user=self.args[0],emo_bool_deleted=False)
    # def render_to_response(self, context, **response_kwargs):
    #     files = [ serialize(p) for p in self.get_queryset() if p.emo_img]
    #     data = {'files': files}
    #     response = JSONResponse(data, mimetype=response_mimetype(self.request))
    #     response['Content-Disposition'] = 'inline; filename=files.json'
    #     return response



class HotEmoListView(ListView):
    model = HotEmos
    context_object_name = "hotemo_cates"
    template_name = "hotemo_manage.html"

    @method_decorator(admin_needed(login_url="/"))
    def dispatch(self, *args, **kwargs):
        return super(HotEmoListView, self).dispatch(*args, **kwargs)
    def post(self, request, *args, **kwargs):
        pass


class HotTagListView(ListView):
    model = HotTags
    context_object_name = "hottag_cates"
    template_name = "hottag_manage.html"

    @method_decorator(admin_needed(login_url="/"))
    def dispatch(self, *args, **kwargs):
        return super(HotTagListView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        pass

@admin_needed(login_url="/")
def AllEmoListView(request,page=1,page_count=20):
    page=request.GET.get('page',None)
    if page==None:
        page=1
    page=int(page)
    object_list=Emotion.objects.filter(emo_bool_deleted=False,emo_img__isnull=False).order_by("-emo_popularity")
    try:
        paginator = Paginator(object_list, page_count) # Show 25 sub_emos per page
    except:
        return ret_status(400)
    flag=3
    try:
        sub_emos = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        sub_emos = paginator.page(page)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        sub_emos = paginator.page(paginator.num_pages)
    return render_to_response("manager_search.html",locals(),context_instance=RequestContext(request))

@admin_needed(login_url="/")
def SearchByAuthor(request,page=1,page_count=20):
    username=request.GET.get('author',None)
    
    page=request.GET.get('page',None)
    if page==None:
        page=1
    page=int(page)
    user_object=get_user_by_username(username)
    flag=1
    
    if user_object==None:
        object_list=None
    else:
        uid=user_object.id
        object_list=Emotion.objects.filter(emo_upload_user=uid,emo_bool_deleted=False,\
            emo_img__isnull=False).order_by("emo_id")
        try:
            paginator = Paginator(object_list, page_count) # Show 25 sub_emos per page
        except:
            return ret_status(400)
        try:
            sub_emos = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            sub_emos = paginator.page(page)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            sub_emos = paginator.page(paginator.num_pages)

    return render_to_response("manager_search.html",locals(),context_instance=RequestContext(request))

@admin_needed(login_url="/")
def SearchByTag(request,page=1,page_count=20):
    tag_name=request.GET.get('tag',None)
    page=request.GET.get('page',None)
    if page==None:
        page=1
    page=int(page)
    cur_tag=get_tag_by_tagname(tag_name)

    flag=2
    if cur_tag==None:
        object_list=None
    else:
        object_list=cur_tag.emo_list.filter(emo_bool_deleted=False,emo_img__isnull=False).\
                order_by("emo_id")

        try:
            paginator = Paginator(object_list, page_count) # Show 25 sub_emos per page
        except:
            return ret_status(400)
        try:
            sub_emos = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            sub_emos = paginator.page(page)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            sub_emos = paginator.page(paginator.num_pages)
    return render_to_response("manager_search.html",locals(),context_instance=RequestContext(request))



@admin_needed(login_url="/")
def list_other_users(request,page=1,page_count=20):

    user_list=SiteUser.objects.all()

    page=request.GET.get('page',None)
    if page==None:
        page=1
    page=int(page)
    try:
        paginator = Paginator(user_list, page_count) # Show 25 sub_emos per page
    except:
        return ret_status(400)
    flag=3
    try:
        sub_users = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        sub_users = paginator.page(page)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        sub_users = paginator.page(paginator.num_pages)
    return render_to_response("list_other_users.html",locals(),context_instance=RequestContext(request))


@admin_needed(login_url="/")
def get_mobile(request):
    return render_to_response("get_mobile.html",locals(),context_instance=RequestContext(request))

@admin_needed(login_url="/")
def get_and_save_vali_code(request):
    mobile=request.GET.get('mobile',None)

    if not mobile:
        message="发生错误，验证码没有发送成功"
    try:
        vali_code_object=ValidationCode()
        cur_datetime=datetime.now()
        vali_code_object.vali_code=str(cur_datetime.microsecond)
        expire_time= cur_datetime+timedelta(3)
        vali_code_object.expire_time=expire_time
        vali_code_object.is_used=False
    except:
        message="发生错误，验证码没有发送成功"
    try:
        num=send_short_message(mobile,vali_code_object.vali_code)
        if num==1:
            message="验证码发送成功"
            vali_code_object.save() 
        else:
            message="发生错误，验证码没有发送成功"
    except:
        message="发生错误，验证码没有发送成功"
    return render_to_response("valicode_status.html",locals(),context_instance=RequestContext(request))












