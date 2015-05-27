search api 

1、按作者搜索表情

/app/search/author=xxx&sortby=1&page=1&count=50

参数分别为：

+   作者，即用户的username，（经过base64编码）
+   返回的表情按照热度|时间排序（1为热度，热度最高的排在最前面；2为时间，最新更新的排在最前面），
+   页码
+   每页返回的数目

失败返回{"status": 400},成功则返回的数据格式如下：

+   {"status": 200,
+   "author":"1110310214",
+   "emos": [
+   {"emo_type": 2, //表情类型
+   "tags": [
+   {"id": 1804, "name": "\u9ad8\u5174","tag_popularity":2},//表情的标签信息
+   {"id": 2221, "name": "happy","tag_popularity":3}
+   ],
+   "emo_id": 2032, //表情ID
+   "emo_detail": "/media/7/1.41904683968e%2B126JmFWDj3UNmMM.gif",//表情位置
+   "is_deleted": false,//是否已删除
+   "emo_popularity": 0,//热度
+   "emo_like": 0,//收藏数
+   "last_update":
+   },
+   ......
+   ],
+   "total_num":300,
+   "next_page":2 //下一页，如果为-1，则不存在下一页
+   }

2、按标签搜索表情

/app/search/tag=xxx&sortby=1&page=1&count=50

参数分别为：

+   标签名（base64编码）
+   返回的表情按照热度|时间排序（1为热度，热度最高的排在最前面；2为时间，最新更新的排在最前面），
+   页码
+   每页返回的数目

失败返回{"status": 400}成功则返回数据格式如下：


+   {"status": 200,
+   "tag":{"id": 2221, "name": "happy","popularity":2,"is_deleted":false,"last_update":1427770195168},//搜索的标签信息
+   "emos": [
+   {"emo_type": 2, //表情类型
+   "emo_id": 2032, //表情ID
+   "emo_detail": "/media/7/1.41904683968e%2B126JmFWDj3UNmMM.gif",//表情位置
+   "emo_author": "nono_1984@163.com",//作者信息
+   "is_deleted": false,//是否已删除
+   "emo_popularity": 0,//热度
+   "emo_like": 0,//收藏数
+   "last_update":1427770195168 //最后更新时间戳
+   },
+   ...
+   ],
+   "total_num":300,//总数
+   "next_page":2//下一页，如果为负值-1，则不存在下一页
+   }

share api

3、将用户的分享信息传回服务器

/app/share/save_share_info

该请求为http POST请求，发送的数据格式如下：
``
{
	"emo_id":"1",
	"share_type":"1",  
}
``

+   其中emo_id为表情id，share_type可取1，2，3，4
+   1表示微信转发，2表示朋友圈分享，3表示微博分享，4表示用户收藏
+   每一次请求成功，emo_populariy数值增加1，相应的分享信息字段也会增加1（即1，2，3，4所代表的类型）

如果成功返回{"status": 200}，否则返回{"status": 400}


4、为每一个表情返回一个html页面用于转发或分享

/app/share/emoid=1

url中参数只包含相应表情的id

如果成功返回包含相应表情的html页面，否则返回{"status": 400}



5.热门标签API：

返回全部热门标签：专辑封面，提供按照时间和热度排序参数


+   /app/gethottags/face_type=1&sort_by=1
+   face_type: 专辑封面：1 最热门表情, 2最新表情 
+   sort_by:1 热度，热度最高的排在最前面，2 时间，最新的标签排在最前

失败返回{"status": 400}成功则返回数据格式如下：

+   {
+      "status":200,           //状态码可以为200,400.200表示成功
+   //400表示失败,失败不传回数据
+      "categories":
+     {//热门标签的类别
+      {"cat_name":足球","tag_list":[{tag_id,tag_name,face_id,face_img},{},{},]}, //标签的类别名，标签列表
+      },
+   }


6.根据拼音返回标签列表api：
+  点击a-z0-9搜索标签：返回每个标签的专辑封面

+  search tags by pinyin: /app/search/tags/pinyin=j&face_type=1&sortby=1&page=1&count=20
+  face_type:封面参数 1表示热度最高的表情，2表示时间最新的表情
+  pinyin:拼音参数
+  sortby:时间和热度排序参数  1 热度  2时间
+  page:页码 -1表示最后一页
+  count:每页标签个数
+  
+  失败返回{"status": 400}成功则返回数据格式如下：
+  
+  {"status": 200, 
+  "next_page": -1, 
+  "total_num": 2, 
+  "tags": [{"tag_name": "\u7ade\u6280\u795e\u5c06", "face_img": "4/1.42909415255e+  12Icon@2x.png", "face_id": 64,  
+   "tag_id": 110}, {"tag_name": "jiang", "face_img": "8/1.4315298803e+  1274.pic.jpg", "face_id": 77, "tag_id": 116}]}


7.模糊搜索标签API：（使用like语法）返回每个标签的专辑封面

+  search tags by word vaguely: /app/search/tags/word=h&face_type=1&sortby=1&page=1&count=20
+  face_type:封面类型 1表示热度最高的表情，2表示时间最新的表情
+  word:模糊词参数
+  sortby:排序 1 热度  2时间
+  page:页码
+  count:每页标签个数
+  
+  失败返回{"status": 400}成功则返回数据格式如下：
+  {"status": 200, 
+  "next_page": -1,
+  "total_num": 2,
+  "tags": [{"tag_name": "haha", "face_img": "4/1.42909412459e+  12Icon@2x.png", "face_id": 63, "tag_id": 86}, 
+  {"tag_name": "bhgfd", "face_img": "5/1.4291038653e+  12lzy@2x.png", "face_id": 72, "tag_id": 100}]}
+  

8.模糊搜索作者API：（使用like语法）返回作者的专辑封面

+  search authors by word vaguely: /app/search/authors/word=哈&face_type=1&sortby=1&page=1&count=20

+  word:模糊词参数
+  sortby:按时间或热度排序参数  1 热度  2时间
+  face_type:封面类型  1表示热度最高的表情，2表示时间最新的表情
+  page:页码
+  count:每页标签个数
+  
+  失败返回{"status": 400}成功则返回数据格式如下：
+  
+  {"status": 200, 
+  "next_page": -1, 
+  "total_num": 3, 
+  "authors": [{"username": "lzy", "face_id": 79, "face_img": "1/1.43153068942e+  1274.pic.jpg"}, {"username": 
+  "lizhongyang", "face_id": 73, "face_img": "2/1.42910529339e+  12lzy@2x.png"}, {"username": "lzyy", "face_id": 71, 
+  "face_img": "3/1.42909968322e+  12Icon@2x.png"}]}


9.输入表情ID，返回表情的全部标签、作者、转发量

+  app/all_emo_info/emoid=1

+  {"weibo_share_num": 0, "emo_popularity": 4, "emo_img": "3/1.42720946481e+  12lzy@2x.png", "author":
+   "lzyy","weixin_send_num": 0, "weixin_share_num": 0, "tag_list": [], "emo_like_num": 4}













