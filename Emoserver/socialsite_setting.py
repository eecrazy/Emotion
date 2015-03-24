# -*- coding: utf-8 -*-

class AccountMixIn(object):
    login_template = 'base_login.html'
    register_template = 'base_login.html'
    reset_passwd_template = 'reset_password.html'
    change_passwd_template = 'change_password.html'
    reset_passwd_email_title = u'逗脸重置密码'
    reset_passwd_email_template = 'reset_password_email.html'



SOCIALOAUTH_SITES = (
    ('douban', 'Emoserver.socialoauth.sites.douban.DouBan', '豆瓣',
        {
          'redirect_uri': 'http://xxx/account/oauth/douban',
          'client_id': '',
          'client_secret': 'e31acd7c94fc31cd',
          'scope': ['douban_basic_common']
        }
    ),
)