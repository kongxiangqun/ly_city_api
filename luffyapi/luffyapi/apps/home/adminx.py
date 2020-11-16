import xadmin
from xadmin import views

class BaseSetting(object):
    """xadmin的基本配置"""
    enable_themes = True  # 开启主题切换功能
    use_bootswatch = True #

xadmin.site.register(views.BaseAdminView, BaseSetting)

class GlobalSettings(object):
    """xadmin的全局配置"""
    site_title = "路飞学城"  # 设置站点标题
    site_footer = "路飞学城有限公司"  # 设置站点的页脚
    menu_style = "accordion"  # 设置菜单折叠

xadmin.site.register(views.CommAdminView, GlobalSettings)

from . import models
class BannerAdmin(object):
    list_display = ['id', 'title', 'link', 'image_url']

xadmin.site.register(models.Banner,BannerAdmin)

class NavXAdmin(object):
    list_display = ['id', 'title', 'link']
    search_fields = ['id', 'title']

xadmin.site.register(models.Nav,NavXAdmin)
