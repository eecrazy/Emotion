#-*- coding=utf-8 -*-
from django import forms
from models import Emotion
from django.contrib.auth.models import User
# class LoginForm(forms.Form):

# 	username = forms.CharField(\
# 		widget=forms.TextInput(\
# 			attrs={'class':'form-control','placeholder':u'用户名'}),
# 		required=True
# 		)

# 	password = forms.CharField(\
# 		widget=forms.PasswordInput(\
# 			attrs={'class':'form-control','placeholder':u'密码'}),
# 			required=True
# 			)

# 	# def clean_username(self):
# 	# 	uname = self.cleaned_data.get("username","")
# 	# 	user = UserProfile.objects.get(user = uname)
# 	# 	if not user:
# 	# 		raise forms.ValidationError(u'用户不存在')
# 	# 	else:
# 	# 		return username


class UploadForm(forms.ModelForm):
	tags = forms.CharField(max_length=500,min_length=1,required=True)
	# username = forms.CharField(max_length=56,required=True)
	class Meta:
		model = Emotion
		fields = ["emo_img"]

class OthersUploadForm(forms.ModelForm):
	tags = forms.CharField(max_length=500,min_length=1,required=True)
	username = forms.CharField(max_length=56,required=True)
	class Meta:
		model = Emotion
		fields = ["emo_img"]

class registerForm(forms.ModelForm):
	email = forms.EmailField(required=True)	
	class Meta:
		model = User
		fields = ["username","password"]
	# username = forms.CharField(max_length=56,required=True)
 	#password



