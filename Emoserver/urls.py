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

	#get hot emo and hot tag
	url(r'^app/gethotemos$',ajax.get_hotemos),
	url(r'^app/gethottags$',ajax.get_hottags),

	#add or remove tag
	url(r'^addtag$',ajax.addtag),
	url(r'^removetag$',ajax.removetag),

	#hottag,hotemo

	url(r'list/hottag$',views.HotTagListView.as_view(),name="list_hottag"),
	url(r'list/hotemo$',views.HotEmoListView.as_view(),name="list_hotemo"),
	url(r'list/sysinfo$',views.sysinfo),
	url(r'create/hotemo$',ajax.CreateHotemo),
	url(r'create/hottag$',ajax.CreateHottag),
	url(r'delete/hotemo$',ajax.DeleteHotemo),
	url(r'delete/hottag$',ajax.DeleteHottag),
	
	#update map
	#^searchbykeyword/(?P<kword>[\w\-]+)
	url(r'^app/updatetemap/cursor=(?P<cursor>[0-9]{13})$',ajax.updatetemap),
	url(r'^app/updateetmap/cursor=(?P<cursor>[0-9]{13})$',ajax.updateetmap),


	#file upload view
	url(r'^upload/new/$', views.PictureCreateView.as_view(), name='upload-new'),
	url(r'^upload/delete/(?P<pk>\d+)$', views.PictureDeleteView.as_view(), name='upload-delete'),
	url(r'^upload/view/$', views.PictureListView.as_view(), name='upload-view'),
	url(r'^userwork/view/(\d+)$', views.UserWorkListView.as_view(), name='userwork-view'),

)

import os
urlpatterns += patterns('',
    (r'^media/(.*)$', 'django.views.static.serve', {'document_root': os.path.join(os.path.abspath(os.path.dirname(__file__)), 'media')}),
)

