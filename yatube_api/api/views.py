from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from rest_framework import viewsets

from api.serializers import CommentSerializer, GroupSerializer, PostSerializer
from posts.models import Comment, Group, Post

STATUS_CODE_MESSAGES = {
    '403_message_for_post': 'Это чужой пост!',
    '403_message_for_comment': 'Это чужой комментарий!',
    '404_message': 'Пост или комментарий не найден.'
}


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        post = self.get_object()
        if self.request.user == post.author:
            return super().perform_update(serializer)
        raise PermissionDenied()

    def perform_destroy(self, instance):
        post = self.get_object()
        if self.request.user == post.author:
            post.delete()
            return super().perform_destroy(instance)
        raise PermissionDenied()


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def get_post(self):
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, pk=post_id)
        return post

    def get_queryset(self):
        return self.get_post().comments.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, post=self.get_post())

    def perform_update(self, serializer):
        comment = self.get_object()
        if self.request.user == comment.author:
            return super().perform_update(serializer)
        raise PermissionDenied()

    def perform_destroy(self, instance):
        comment = self.get_object()
        if self.request.user == comment.author:
            return super().perform_destroy(instance)
        raise PermissionDenied()
