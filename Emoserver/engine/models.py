from django.db import models
#from django.contrib.auth.models import User
from Emoserver.users.models import SiteUser
import time
# Create your models here.



# def user_img_url(instance,filename):
# 	return '/'.join(['avatar',str(instance.user.pk)])

# class UserProfile(models.Model):
# 	#user login information
# 	user = models.OneToOneField(User)
# 	#u_id = models.AutoField(primary_key=True)
# 	#u_name = models.CharField(max_length=128,unique=True,db_index=True)
# 	#u_pass = models.CharField(max_length=128)
# 	#u_type = models.PositiveSmallIntegerField(choices=USER_TYPE)


# 	#user profile
# 	#u_email = models.EmailField(blank=False)
# 	u_personal_url = models.CharField(max_length=256,blank=True)
# 	u_weibo_url = models.CharField(max_length=256,blank=True)
# 	u_douban_url = models.CharField(max_length=256,blank=True)


# 	#third party login generate region
# 	u_avatar_img = models.ImageField(upload_to=user_img_url,blank=True)
# 	u_thirdparty_type = models.PositiveSmallIntegerField(blank=True)
# 	u_thirdparty_token = models.CharField(max_length=128,blank=True)

# 	def __unicode__(self):
# 		return self.user.username


	#u_register_time = models.BigIntegerField(default=time.time()*1000,db_index=True)


class Tag(models.Model):

	tag_id = models.AutoField(primary_key=True)
	tag_name = models.CharField(max_length=255,unique=True,db_index=True)
	tag_popularity = models.IntegerField(default=0,db_index=True)
	tag_last_update = models.BigIntegerField(db_index=True)
	tag_bool_deleted = models.BooleanField(default=False)
	# is_hot_tag = models.BooleanField(default=False)
	pinyin=models.CharField(max_length=2,db_index=True)


	def save(self,*args,**kwargs):
		self.tag_last_update = time.time()*1000
		super(Tag,self).save(*args,**kwargs)

	def __str__(self):
		return self.tag_name




# class Picture(models.Model):
#     """This is a small demo using just two fields. The slug field is really not
#     necessary, but makes the code simpler. ImageField depends on PIL or
#     pillow (where Pillow is easily installable in a virtualenv. If you have
#     problems installing pillow, use a more generic FileField instead.

#     """
#     file = models.ImageField(upload_to="pictures")
#     tags = models.TextField(blank=False)

#     def __unicode__(self):
#         return self.file.name

#     @models.permalink
#     def get_absolute_url(self):
#         return ('upload-new', )

#     def save(self, *args, **kwargs):
#         #self.slug = self.file.name
#         super(Picture, self).save(*args, **kwargs)

#     def delete(self, *args, **kwargs):
#         """delete -- Remove to leave file."""
#         self.file.delete(False)
#         super(Picture, self).delete(*args, **kwargs)


def get_emoimg_url(instance,filename):
    return '/'.join([str(instance.emo_upload_user.pk),str(time.time()*1000) + filename])

class Emotion(models.Model):


	EMO_TYPE_CHOICES = ((1,"text"),(2,"motion"))

	emo_id = models.AutoField(primary_key=True)
	emo_type = models.PositiveSmallIntegerField(choices=EMO_TYPE_CHOICES)

	#store the image content
	emo_img = models.ImageField(upload_to=get_emoimg_url,blank=True)
	emo_content = models.TextField(blank=True)

	emo_upload_user = models.ForeignKey(SiteUser)
	#all the tags
	emo_tag_list = models.ManyToManyField(Tag,related_name="emo_list")
	#the tags tagged by the upload user 
	emo_init_tag_list = models.ManyToManyField(Tag,related_name="emo_init_list")

	emo_popularity = models.IntegerField(default=0)
	emo_like_num = models.IntegerField(default=0)
	weibo_share_num = models.IntegerField(default=0)
	weixin_share_num = models.IntegerField(default=0)
	weixin_send_num = models.IntegerField(default=0)

	emo_bool_deleted = models.BooleanField(default=False)
	emo_last_update = models.BigIntegerField(db_index=True)

	def save(self, *args, **kwargs):
		self.emo_last_update = time.time()*1000
		super(Emotion,self).save(*args,**kwargs)

	@models.permalink
	def get_absolute_url(self):
		return ('upload-new', )

	def delete(self, *args, **kwargs):
		"""delete -- Remove to leave file."""
		self.emo_img.delete(False)
		super(Emotion, self).delete(*args, **kwargs)


#the emotion that user have collect
class UserLikeCollection(models.Model):
	user = models.ForeignKey(SiteUser)
	user_like_emotion = models.ManyToManyField(Emotion,related_name="user_like")

class HotTags(models.Model):
	hottag_id = models.AutoField(primary_key=True)
	hottag_category = models.CharField(max_length=64)
	hottag_list = models.ManyToManyField(Tag,related_name="htag") 



class HotEmos(models.Model):
	hotemo_id = models.AutoField(primary_key=True)
	hotemo_category = models.CharField(max_length=64)
	hotemo_list = models.ManyToManyField(Emotion,related_name="hemo")

