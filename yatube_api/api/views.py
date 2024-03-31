from django.http import Http404
from django.shortcuts import get_object_or_404

from rest_framework import viewsets, status
from rest_framework.response import Response

from posts.models import Comment, Group, Post
from .serializers import CommentSerializer, PostSerializer, GroupSerializer

STATUS_CODE_MESSAGES = {
    '405_message': 'Отказано в доступе',
    '403_message_for_post': 'Это чужой пост!',
    '403_message_for_comment': 'Это чужой комментарий!',
    '404_message': 'Пост или комментарий не найден.'
}


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    def get_queryset(self):
        if self.action in ['list', 'retrieve']:
            return Group.objects.all()
        return Group.objects.none()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return GroupSerializer
        return None

    def create(self, request):
        if not request.user.is_staff:
            return Response(
                STATUS_CODE_MESSAGES['405_message'],
                status=status.HTTP_405_METHOD_NOT_ALLOWED
            )
        return super().create(request)


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def list(self, request):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        post = self.get_object()
        serializer = self.serializer_class(post)
        return Response(serializer.data)

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save(author=self.request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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

    def list(self, request, post_id=None):
        post = get_object_or_404(Post, pk=post_id)
        comments = post.comments.all()
        serializer = self.serializer_class(
            comments,
            many=True
        )
        return Response(serializer.data)

    def perform_create(self, serializer):
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, pk=post_id)
        serializer.save(author=self.request.user, post=post)

    def retrieve(self, request, post_id=None, pk=None):
        post = get_object_or_404(Post, pk=post_id)
        comment = get_object_or_404(post.comments.all(), pk=pk)
        serializer = self.serializer_class(comment)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # Методы для PUT, PATCH и DELETE запросов для комментариев сделаны криво,
    # т.к. тесты не проходили с реализацией, аналогичной постам

    def update(self, request, post_id=None, pk=None):
        try:
            post = get_object_or_404(Post, pk=post_id)
            comment = get_object_or_404(post.comments.all(), pk=pk)
        except Http404:
            return Response(
                STATUS_CODE_MESSAGES['404_message'],
                status=status.HTTP_404_NOT_FOUND
            )

        if request.user == comment.author:
            serializer = self.serializer_class(comment, data=request.data)
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
        try:
            post = get_object_or_404(Post, pk=post_id)
            comment = get_object_or_404(post.comments.all(), pk=pk)
        except Http404:
            return Response(
                STATUS_CODE_MESSAGES['404_message'],
                status=status.HTTP_404_NOT_FOUND
            )

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
        try:
            post = get_object_or_404(Post, pk=post_id)
            comment = get_object_or_404(post.comments.all(), pk=pk)
        except Http404:
            return Response(
                STATUS_CODE_MESSAGES['404_message'],
                status=status.HTTP_404_NOT_FOUND
            )

        if request.user == comment.author:
            comment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                STATUS_CODE_MESSAGES['403_message_for_comment'],
                status=status.HTTP_403_FORBIDDEN
            )
