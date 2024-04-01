from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response

from posts.models import Comment, Group, Post
from api.serializers import CommentSerializer, PostSerializer, GroupSerializer

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

    def update(self, request, pk=None):
        post = self.get_object()
        serializer = self.serializer_class(post, data=request.data)
        if serializer.is_valid():
            if self.request.user == post.author:
                serializer.save()
                return Response(serializer.data)
            return Response(
                STATUS_CODE_MESSAGES['403_message_for_post'],
                status=status.HTTP_403_FORBIDDEN
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        post = self.get_object()
        serializer = self.serializer_class(
            post,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            if self.request.user == post.author:
                serializer.save()
                return Response(serializer.data)
            return Response(
                STATUS_CODE_MESSAGES['403_message_for_post'],
                status=status.HTTP_403_FORBIDDEN
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        post = self.get_object()
        if self.request.user == post.author:
            post.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            STATUS_CODE_MESSAGES['403_message_for_post'],
            status=status.HTTP_403_FORBIDDEN
        )


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

    def update(self, request, post_id=None, pk=None):
        comment = self.get_object()
        if request.user == comment.author:
            serializer = self.serializer_class(
                comment,
                data=request.data
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        else:
            return Response(
                STATUS_CODE_MESSAGES['403_message_for_comment'],
                status=status.HTTP_403_FORBIDDEN
            )

    def partial_update(self, request, post_id=None, pk=None):
        comment = self.get_object()
        if request.user == comment.author:
            serializer = self.serializer_class(
                comment,
                data=request.data,
                partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        else:
            return Response(
                STATUS_CODE_MESSAGES['403_message_for_comment'],
                status=status.HTTP_403_FORBIDDEN
            )

    def destroy(self, request, post_id=None, pk=None):
        comment = self.get_object()
        if request.user == comment.author:
            comment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                STATUS_CODE_MESSAGES['403_message_for_comment'],
                status=status.HTTP_403_FORBIDDEN
            )
