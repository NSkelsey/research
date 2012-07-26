from django.conf.urls import patterns, include, url
from front import views

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$',  views.home),
    url(r'^simple_form$',  views.simple_form),
    url(r'^db_view$', views.raw_req),
    url(r'^select_builder$', views.select_builder),
    url(r'^xhr$', views.xhr),
    url(r'^gdft_xhr$', views.gdft_xhr),
    url(r'out_form', views.out_form),
    url(r'jsfun', views.hit_js),
    url(r'dbs', views.present_dbs),
    url(r'filter/(?P<filter_name>\S+)/delete$', views.delete_filter),
    url(r'filter/(?P<filter_name>\S+)/$', views.show_filter),
    url(r'filter/(?P<filter_name>\S+)/save$', views.save_filter),
    url(r'filter/(?P<filter_name>\S+)/expression$', views.show_expression),
    # url(r'^ajax_time/', include('ajax_time.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
