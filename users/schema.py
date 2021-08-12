from django.contrib.auth import get_user_model

import graphene
from graphene_django import DjangoObjectType


class UserType(DjangoObjectType):
    class Meta:
        model = get_user_model()


class CreateUser(graphene.Mutation):
    user = graphene.Field(UserType)

    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)
        password_confirmation = graphene.String(required=True)
        email = graphene.String(required=True)

    def mutate(self, info, username, password, password_confirmation, email):
        user = get_user_model()(
            username=username,
            email=email,
        )
        if password == password_confirmation:
            user.set_password(password)
            user.save()

            return CreateUser(user=user)
class UpdateUser(graphene.Mutation):
    user = graphene.Field(UserType)

    class Arguments:
        username = graphene.String()
        password = graphene.String()
        email = graphene.String()
        id = graphene.ID()

    def mutate(self, info, username, password, email, id):
        user = info.context.user
        check_owner = ((user.id, int(id)))
        # print(check_owner)
        if user.is_authenticated and check_owner[0] == check_owner[1]:
            user = get_user_model()(id=id, username=username, email=email)
            user.set_password(password)
            user.save()

            return UpdateUser(user=user)
        raise Exception("user must be signed in to their account")
class SignOut(graphene.Mutation):
    user = graphene.Field(UserType)

    class Arguments:
        id = graphene.ID()
    
    def mutate(self, info, id):
        user = info.context.user

        check_owner = (user.id, int(id))
        if user.is_authenticated and check_owner[0] == check_owner[1]:
            print('signed out')
            return SignOut(
                user=user
            )

class Query(graphene.ObjectType):
    me = graphene.Field(UserType)
    users = graphene.List(UserType)

    def resolve_users(self, info):
        return get_user_model().objects.all()

    def resolve_me(self, info):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('Not logged in')

        return user

class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    update_user = UpdateUser.Field()
    sign_out = SignOut.Field()
