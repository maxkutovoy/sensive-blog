from django.db.models import Count
from django.shortcuts import render
from blog.models import Comment, Post, Tag


def get_related_posts_count(tag):
    return tag.posts.count()


def get_publish_date(post):
    return post.published_at


def serialize_post(post):
    return {
        'title': post.title,
        'teaser_text': post.text[:200],
        'author': post.author.username,
        'comments_amount': len(Comment.objects.filter(post=post)),
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in post.tags.all()],
        'first_tag_title': post.tags.all()[0].title,
    }


def serialize_post_optimized(post):
    return {
        'title': post.title,
        'teaser_text': post.text[:200],
        'author': post.author.username,
        'comments_amount': post.comments_count,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in post.tags.all()],
        'first_tag_title': post.tags.all()[0].title,
    }


def serialize_tag(tag):
    return {
        'title': tag.title,
        'posts_with_tag': len(Post.objects.filter(tags=tag)),
    }


def get_likes_count(post):
    return post.likes.count()


def index(request):
    most_popular_posts = Post.objects.annotate(
        likes_count=Count('likes')).order_by('-likes_count').prefetch_related(
        'author')
    most_popular_posts_ids = [post.id for post in most_popular_posts]

    posts_with_comments = Post.objects.filter(
        id__in=most_popular_posts_ids).annotate(
        comments_count=Count('comments')).prefetch_related('author')
    ids_and_comments = posts_with_comments.values_list('id', 'comments_count')
    count_for_id = dict(ids_and_comments)

    most_fresh_posts = most_popular_posts.order_by('published_at')
    most_fresh_posts = list(most_fresh_posts)[-5:]

    for post in most_popular_posts:
        if post in most_fresh_posts:
            fresh_post_index = most_fresh_posts.index(post)
            most_fresh_posts[fresh_post_index].comments_count = count_for_id[
                post.id]
        post.comments_count = count_for_id[post.id]

    most_popular_tags = Tag.objects.popular()[:5]
    most_popular_posts = list(most_popular_posts)[:5]

    context = {
        'most_popular_posts': [
            serialize_post_optimized(post) for post in most_popular_posts
        ],
        'page_posts': [serialize_post_optimized(post) for post in
                       most_fresh_posts],
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
    }
    return render(request, 'index.html', context)


def post_detail(request, slug):
    post = Post.objects.get(slug=slug)
    comments = Comment.objects.filter(post=post)
    serialized_comments = []
    for comment in comments:
        serialized_comments.append({
            'text': comment.text,
            'published_at': comment.published_at,
            'author': comment.author.username,
        })

    likes = post.likes.all()

    related_tags = post.tags.all()

    serialized_post = {
        'title': post.title,
        'text': post.text,
        'author': post.author.username,
        'comments': serialized_comments,
        'likes_amount': len(likes),
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in related_tags],
    }

    most_popular_tags = Tag.objects.popular()[:5]
    most_popular_posts = []  # TODO. Как это посчитать?

    context = {
        'post': serialized_post,
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
        'most_popular_posts': [
            serialize_post_optimized(post) for post in most_popular_posts
        ],
    }
    return render(request, 'post-details.html', context)


def tag_filter(request, tag_title):
    tag = Tag.objects.get(title=tag_title)

    most_popular_posts = Post.objects.annotate(
        likes_count=Count('likes')).order_by('-likes_count').prefetch_related(
        'author')
    most_popular_posts_ids = [post.id for post in most_popular_posts]

    posts_with_comments = Post.objects.filter(
        id__in=most_popular_posts_ids).annotate(
        comments_count=Count('comments')).prefetch_related('author')
    ids_and_comments = posts_with_comments.values_list('id', 'comments_count')
    count_for_id = dict(ids_and_comments)

    related_posts = list(most_popular_posts.filter(tags__title=tag_title))[:20]

    for post in most_popular_posts:
        if post in related_posts:
            related_post_index = related_posts.index(post)
            related_posts[related_post_index].comments_count = count_for_id[
                post.id]
        post.comments_count = count_for_id[post.id]

    most_popular_tags = Tag.objects.popular()[:5]
    most_popular_posts = list(most_popular_posts)[:5]


    # posts = Post.objects.annotate(
    #     likes_count=Count('likes', distinct=True), comments_count=Count(
    #         'comments', distinct=True)).prefetch_related('author')
    #
    # most_popular_tags = Tag.objects.popular()[:5]
    #
    # popular_posts = posts.order_by('-likes_count')
    # most_popular_posts = list(popular_posts)[:5]
    #
    # related_posts = posts.filter(tags__title=tag_title)[:20]

    context = {
        'tag': tag.title,
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
        'posts': [serialize_post_optimized(post) for post in related_posts],
        'most_popular_posts': [
            serialize_post_optimized(post) for post in most_popular_posts
        ],
    }
    return render(request, 'posts-list.html', context)


def contacts(request):
    # позже здесь будет код для статистики заходов на эту страницу
    # и для записи фидбека
    return render(request, 'contacts.html', {})
