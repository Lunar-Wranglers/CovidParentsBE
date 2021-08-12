from django.contrib import auth
import graphene
from graphene_django import DjangoObjectType
from users.schema import UserType

from .models import Link
from .models import Image
from .models import Post

class LinkType(DjangoObjectType):
    class Meta:
        model = Link
class ImageType(DjangoObjectType):
    class Meta:
        model = Image
        filter_fields = ["image"]
class PostType(DjangoObjectType):
    class Meta:
        model = Post

class Query(graphene.ObjectType):
    links = graphene.List(LinkType)
    my_links = graphene.List(LinkType)
    all_images = graphene.List(ImageType)
    all_posts = graphene.List(PostType)
    my_posts = graphene.List(PostType)
    image = graphene.Field(ImageType, id=graphene.Int(required=True))


    def resolve_my_links(self, info):
        # queries only the links they own
        if not info.context.user.is_authenticated:
            return Link.objects.none()
        else:
            return Link.objects.filter(owner=info.context.user)
    def resolve_links(self, info, **kwargs):
        return Link.objects.all()
    def resolve_all_images(self, info, **kwargs):
        return Image.objects.all()
    def resolve_image(self, info, id):
        return Image.objects.get(id=id)
    def resolve_all_posts(self, info):
        return Post.objects.all()
    def resolve_my_posts(self, info):
        # queries only the links they own
        if not info.context.user.is_authenticated:
            return Post.objects.none()
        else:
            return Post.objects.filter(owner=info.context.user)

class CreateLink(graphene.Mutation):
    id = graphene.ID()
    url = graphene.String()
    description = graphene.String()
    owner = graphene.Field(UserType)

    class Arguments:
        url = graphene.String()
        description = graphene.String()

    def mutate(self, info, url, description):
        user = info.context.user or None
        if user.is_authenticated:
            link = Link(url=url, description=description, owner=user)
            link.save()
            return CreateLink(
                    id=link.id,
                    url=link.url,
                    description=link.description,
                    owner=link.owner,
            )
        raise Exception('Please Log In')

class UpdateLink(graphene.Mutation):
    id = graphene.ID()
    url = graphene.String()
    description = graphene.String()
    owner = graphene.Field(UserType)


    class Arguments:
        id = graphene.ID()
        url = graphene.String()
        description = graphene.String()
        
    def mutate(self, info, url, description, id):
        # get the user object from the request (info.context)
        user = info.context.user
        # This provides a query set of the values of all of the users owned links
        owner = Link.objects.filter(owner=info.context.user, id=id).values_list('owner_id', flat=True)
        # print(list(owner)[0])
        # iterate through the links
        # for owner in owner_links:
        #     # first we extract the owner as a list
        #     owner = list(owner.values())
        #     # the owner is the last value in the list
        #     owned_id = (owner[0])

        #     # print([owned_id, int(id)])
        #     # create a list to store the values of the id in the list of owned ids and the id passed in
        #     is_owner = (owned_id, int(id))
        #     # compare the id of the owned links to the id passed in and if the user is logged in
        #     if is_owner[0] == is_owner[1] and user.is_authenticated:
                # print('authorized')
                # mutate the link based on the arguments below
        if len(list(owner)) == 0:
            raise Exception('Not authorized to update this link')
        elif list(owner)[0] == user.id:
            link = Link(id=id, url=url, description=description, owner=user)
            # save the link
            link.save()
            # then return it
            return UpdateLink(
                id=link.id,
                url=link.url,
                description=link.description,
                owner=link.owner
            )
        raise Exception('Not authorized to update this link. Please sign in or try a different link.')
class DeleteLink(graphene.Mutation):
    id = graphene.Int()

    class Arguments:
        id = graphene.Int()

    def mutate(self, info, id):
        # get the user object from the request (info.context)
        user = info.context.user
        # This provides a query set of the values of all of the users owned links
        owner = Link.objects.filter(owner=info.context.user, id=id).values_list('owner_id', flat=True)
        # print(list(owner)[0])
        # iterate through the links
        # for owner in owner_links:
        #     # first we extract the owner as a list
        #     owner = list(owner.values())
        #     # the owner is the last value in the list
        #     owned_id = (owner[0])

        #     # print([owned_id, int(id)])
        #     # create a list to store the values of the id in the list of owned ids and the id passed in
        #     is_owner = (owned_id, int(id))
        #     # compare the id of the owned links to the id passed in and if the user is logged in
        #     if is_owner[0] == is_owner[1] and user.is_authenticated:
                # print('authorized')
                # mutate the link based on the arguments below
        if len(list(owner)) == 0:
            raise Exception('Not authorized to delete this link')
        elif list(owner)[0] == user.id:
            link = Link(id=id)
            link.delete()

            return DeleteLink(
                id=link.id      
            )
        raise Exception('Not authorized to delete this link. Please sign in or try a different link.')
class CreatePost(graphene.Mutation):
    id = graphene.ID()
    title = graphene.String()
    description = graphene.String()
    image = graphene.Field(ImageType)
    updated_at = graphene.DateTime()
    owner = graphene.Field(UserType)

    class Arguments:
        title = graphene.String()
        description = graphene.String()
        
    def mutate(self, info, title, description):
        user = info.context.user
        files = info.context.FILES['image']
        post = Post(title=title, description=description, image=files, owner=user)
        if user.is_authenticated:
            post.save()
            return CreatePost(
                id=post.id,
                title=post.title,
                description=post.description,
                image=post.image,
                updated_at=post.updated_at,
                owner=post.owner
            )
class UpdatePost(graphene.Mutation):
    id = graphene.ID()
    title = graphene.String()
    description = graphene.String()
    image = graphene.String()
    updated_at = graphene.DateTime()
    owner = graphene.Field(UserType)

    class Arguments:
        id = graphene.ID()
        title = graphene.String()
        description = graphene.String()
        
    def mutate(self, info, id, title, description):
        user = info.context.user
        files = info.context.FILES['image']
        owner = Post.objects.filter(owner=user, id=id).values_list('owner_id', flat=True)
        if len(list(owner)) == 0:
            raise Exception('Not authorized to update this post')
        elif list(owner)[0] == user.id:
            post = Post(id=id, title=title, description=description, image=files, owner=user)
            post.save()
            return UpdatePost(
                id=post.id,
                title=post.title,
                description=post.description,
                image=post.image,
                updated_at=post.updated_at,
                owner=post.owner
            )        
class DeletePost(graphene.Mutation):
    id = graphene.ID()

    class Arguments:
        id = graphene.ID()
        
    def mutate(self, info, id):
        user = info.context.user
        owner = Post.objects.filter(owner=user, id=id).values_list('owner_id', flat=True)
        if len(list(owner)) == 0:
            raise Exception('Not authorized to delete this post')
        elif list(owner)[0] == user.id:
            post = Post(id=id)
            post.delete()
            return DeletePost(
                id=post.id
            )        

class Mutation(graphene.ObjectType):
    create_link = CreateLink.Field()
    update_link = UpdateLink.Field()
    delete_link = DeleteLink.Field()
    create_post = CreatePost.Field()
    update_post = UpdatePost.Field()
    delete_post = DeletePost.Field()