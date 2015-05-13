from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from engine import views
from engine import ajax

urlpatterns = patterns('',
	url(r'^$',views.index),
	# url(r'^login$',views.mylogin),
	# url(r'^loginout$',views.loginout),
	# url(r'^register$',views.UserCreateView.as_view(),name="create-user"),
	url(r'^test$',views.test),
	
	url(r'', include('Emoserver.users.urls')),
	url(r'^anotate_emo/$',ajax.annoate_emotion),

	#search API
	#search emos by author
	#/app/search/author=xxx&sortby=1&page=1&count=50
	url(r'^app/search/author=(?P<username>.*)&sortby=(?P<sortby>[1-2]{1})&page=(?P<page>\d+)&count=(?P<page_count>\d+)$',ajax.search_emos_by_author),
	#search emos by tag
	#/app/search/tag=xxx&sortby=1&page=1&count=50
	url(r'^app/search/tag=(?P<tag_name>.*)&sortby=(?P<sortby>[1-2]{1})&page=(?P<page>\d+)&count=(?P<page_count>\d+)$',ajax.search_emos_by_tag),



	#search tags by pinyin: /app/search/tags/pinyin=a&face_type=1&sortby=1&page=1&count=20
	url(r'^app/search/tags/pinyin=(?P<pinyin>.*)&face_type=(?P<face_type>[1-2]{1})&sortby=(?P<sortby>[1-2]{1})&page=(?P<page>\d+)&count=(?P<page_count>\d+)$',ajax.search_tags_by_pinyin),

	#search tags by word vaguely: /app/search/tags/word=hh&face_type=1&sortby=1&page=1&count=20
	url(r'^app/search/tags/word=(?P<word>.*)&face_type=(?P<face_type>[1-2]{1})&sortby=(?P<sortby>[1-2]{1})&page=(?P<page>\d+)&count=(?P<page_count>\d+)$',ajax.search_tags_by_vaguely_word),

	#search authors by word vaguely: /app/search/authors/word=hh&face_type=1&sortby=1&page=1&count=20
	url(r'^app/search/authors/word=(?P<word>.*)&face_type=(?P<face_type>[1-2]{1})&sortby=(?P<sortby>[1-2]{1})&page=(?P<page>\d+)&count=(?P<page_count>\d+)$',ajax.search_authors_by_vaguely_word),


	#return the emo html to share 
	url(r'^app/share/emoid=(?P<emoid>\d+)$',ajax.get_emo_html),

	#return all emo info about a emo 
	url(r'^app/all_emo_info/emoid=(?P<emoid>\d+)$',ajax.get_all_emo_info),

	#save the emo share info 
	url(r'^app/share/save_share_info$',ajax.save_share_info),

	#get hot emo and hot tag
	url(r'^app/gethotemos$',ajax.get_hotemos),

	# /app/gethottags/face_type=1&sort_by=1
	url(r'^app/gethottags/face_type=(?P<face_type>[1-2]{1})&sort_by=(?P<sort_by>[1-2]{1})$',ajax.get_hottags),

	#add or remove tag
	url(r'^addtag$',ajax.addtag),
	url(r'^removetag$',ajax.removetag),


	#hottag,hotemo
	url(r'list/hottag$',views.HotTagListView.as_view(),name="list_hottag"),
	url(r'list/hotemo$',views.HotEmoListView.as_view(),name="list_hotemo"),
	url(r'list/sysinfo$',views.sysinfo),
	url(r'create/hotemo$',ajax.CreateHotemo),
	url(r'create/hottag$',ajax.CreateHottag),
	url(r'addhottag$',ajax.AddHottag),
	url(r'delete/hotemo$',ajax.DeleteHotemo),
	url(r'delete/hottag$',ajax.DeleteHottag),
	url(r'removehottag$',ajax.RemoveHottag),

	#admin search
	url(r'^search/view/$', views.AllEmoListView, name='search_view'),
    url(r'^get/mobile$', views.get_mobile),
	url(r'^search/author$', views.SearchByAuthor, name='search_by_author_view'),
	url(r'^search/tag.*$', views.SearchByTag, name='search_by_tag_view'),

	#get validation code
	url(r'^get/valicode$', views.get_and_save_vali_code, name="get_and_save_vali_code"),
 
	#update map
	#^searchbykeyword/(?P<kword>[\w\-]+)
	url(r'^app/updatetemap/cursor=(?P<cursor>[0-9]{13})$',ajax.updatetemap),
	url(r'^app/updateetmap/cursor=(?P<cursor>[0-9]{13})$',ajax.updateetmap),


	#file upload view
	url(r'^upload/new/$', views.PictureCreateView.as_view(), name='upload-new'),
	url(r'^upload/delete/(?P<pk>\d+)$', views.PictureDeleteView.as_view(), name='upload-delete'),
	url(r'^upload/view/$', views.PictureListView, name='upload-view'),
	url(r'^userwork/view/(\d+)$', views.UserWorkListView.as_view(), name='userwork-view'),

	#admin add emo for other users
	url(r'^addemo/add/author=(?P<author>.*)$', views.CreateemoForOthers.as_view()),
	url(r'^addemo/view$', views.list_other_users),



)

import os
urlpatterns += patterns('',
    (r'^media/(.*)$', 'django.views.static.serve', {'document_root': os.path.join(os.path.abspath(os.path.dirname(__file__)), 'media')}),
)

