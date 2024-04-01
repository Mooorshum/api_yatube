
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views

from api.views import CommentViewSet, GroupViewSet, PostViewSet


router_v1 = DefaultRouter()
router_v1.register(r'posts', PostViewSet)
router_v1.register('groups', GroupViewSet)
router_v1.register(r'comments', CommentViewSet, basename='comments')

urlpatterns = [
    path('api/v1/', include(router_v1.urls)),
    path('api/v1/posts/<int:post_id>/', include(router_v1.urls)),
    path('api/v1/api-token-auth/', views.obtain_auth_token),
]
