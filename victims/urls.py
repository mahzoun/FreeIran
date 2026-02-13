from django.urls import include, path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("victims/", views.victim_list, name="victim_list"),
    path("victims/<slug:slug>/", views.victim_detail, name="victim_detail"),
    path("submit/", views.submit_correction, name="submit_correction"),
    path(
        "submit/<slug:slug>/",
        views.submit_correction,
        name="submit_correction_for_victim",
    ),
    path("disclaimer/", views.disclaimer, name="disclaimer"),
    path("api/", include("victims.api_urls")),
]
