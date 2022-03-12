from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from .views import (add_comment, follow_index, group_posts, index, post_create,
                    post_detail, post_edit, profile, profile_follow,
                    profile_unfollow)

app_name = 'posts'

urlpatterns = [
    path('', index, name='index'),
    path('create/', post_create, name='post_create'),
    path('follow/', follow_index, name='follow_index'),
    path('group/<slug:slug>/', group_posts, name='group_post'),
    path('posts/<int:post_id>/', post_detail, name='post_detail'),
    path('posts/<int:post_id>/comment/', add_comment, name='add_comment'),
    path('posts/<int:post_id>/edit/', post_edit, name='post_edit'),
    path('profile/<str:username>/', profile, name='profile'),
    path('profile/<str:username>/follow/',
         profile_follow,
         name='profile_follow'),
    path('profile/<str:username>/unfollow/',
         profile_unfollow,
         name='profile_unfollow'),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
