from rest_framework import serializers
from django.contrib.auth import authenticate
from account.models import User
from django.utils.encoding import smart_str, force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator


"""
The password2 field in your UserRegistationSerializer should be a serializers.CharField instead of a models.CharField. The serializers.CharField is used to define how the field should be serialized, whereas models.CharField is used to define how the field should be stored in the database.
"""


class UserRegistationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(
        style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = ['email', 'name', 'password', 'password2']
        # we have to mention password2 in usermanager create_user function
        extra_kwargs = {
            'password': {'write_only': True}
        }

        """The extra_kwargs option is used to provide additional arguments to a serializer field,
         and is used here to specify that the password field should be write-only. 
         This means that the field will be included in requests to create or update a user, 
         but will not be returned in response data, for security reasons.If extra_kwargs is not used, 
         then the default behavior for the password field will be used. By default, 
         a serializer field is read-write, meaning that it can both receive and return data. 
         If the password field were read-write, then the password would be included in the response data, 
         which could be a security risk."""

        """In the other hand, the password2 field is also write-only, 
        but it is not included in the extra_kwargs dictionary. 
        This is because password2 is not a field of the User model. 
        Instead, it is a custom field that is used to confirm the password. 
        Therefore, it does not need to be specified in extra_kwargs."""

    # is_valid() function run garda you function run huncha
    def validate(self, attrs):
        # attrs is data. the data in serializer >>>data<<<< = request.data
        password = attrs.get('password')
        password2 = attrs.get('password2')

        """If you remove raise serializers.ValidationError and replace it with return Response({...}),
        the serializer validation will not fail anymore, and instead,
        it will return a Response object with a dictionary of errors.
        This is not the correct behavior because when the serializer validation fails,
        it should raise an exception and prevent the view from continuing.
        By returning a Response object with the error dictionary,
        the view will continue executing, and it may lead to unexpected behavior or errors in the rest of the code.
        It is also not following the RESTful design principles, where you should return the appropriate HTTP status codes and error messages to indicate the error.So, it's best to keep the raise serializers.ValidationError statement in the validate method to ensure that the serializer validation fails when the input data is invalid."""

        if password != password2:
            raise serializers.ValidationError(
                'Password and Comform password does not match')

        # if both password is same data will be avaliable or miljayega
        return attrs

    def create(self, validated_data):
        # validated_data.pop('password2', None)
        # the order of fields in the fields attribute of your serializer should match the order of parameters in the create_user method.
        user = User.objects.create_user(**validated_data)
        # it unpacks the values from the dictionary as keyword arguments to the function. 
        return user

        """**validate_data is used to unpack a dictionary of validated data into keyword arguments for a function call. """

        """
        If you remove the create() method from your serializer,
        you will get an AttributeError when you try to create an instance of your serializer.
        This is because Django REST Framework 
        requires a create() method to be defined in the serializer in order to create new objects.
        The create() method is responsible for creating a new instance of the model 
        using the validated data that was passed to the serializer. It receives the validated data as a dictionary and should return a new instance of the model with the data applied.
        If you remove the create() method,
        Django REST Framework will not know how to create a new instance of the model and will raise an AttributeError.
        So it's important to make sure that your serializer includes a create() method,
        even if it's just a default implementation that does nothing.
        """


class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255)
    """If the email field is defined in the User model and is not being modified during the login process,
    it may be more appropriate to remove the email field from the UserLoginSerializer and 
    extract it directly from request.data in the UserLoginView.
    This approach avoids the unnecessary validation and deserialization of the email field in the serializer,
    and can make the code more concise and easier to understand.
    On the other hand, if you need to validate and deserialize other fields in the request data,
    or if the email field needs to be modified or transformed during the login process,
    it may be more appropriate to keep the email field in the UserLoginSerializer and 
    extract it using serializer.data.get('email')."""
    class Meta:
        model = User
        fields = ['email', 'password']


"""The reason you need to define email in the serializer even though it's already in the User model is that the serializer defines the structure of the data that is being sent to the server.
In this case, the UserLoginSerializer is used to serialize and validate the data sent from the client-side to the server-side during login. It expects the data to have an email field and a password field.
If you don't define the email field in the serializer, the serializer won't be able to validate the email field in the incoming data, and hence the validation fails, and it throws the error "user with this email already exists."
However, when you define the email field in the serializer, the serializer is able to validate the email field in the incoming data, and if it's valid, the authentication process happens, and you get the response "Login Successful."
So, even though the email field is already defined in the User model, you still need to define it in the serializer as well to ensure that the incoming data is validated correctly."""


class UserProfileViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email']


class UserChangePasswordViewSerializer(serializers.Serializer):
    old_password = serializers.CharField(
        max_length=255, style={'input_type': 'password'}, write_only=True)
    password = serializers.CharField(
        max_length=255, style={'input_type': 'password'}, write_only=True)
    password2 = serializers.CharField(
        max_length=255, style={'input_type': 'password'}, write_only=True)

    class Meta:
        fields = ['old_password', 'password', 'password2']

    def validate(self, attrs):
        old_password = attrs.get('old_password')
        password = attrs.get('password')
        password2 = attrs.get('password2')
        user = self.context.get('user')

        if password != password2:
            raise serializers.ValidationError(
                "Password and Confirm Password don't match")

        # Check if the old password matches the user's current password
        if not authenticate(username=user.email, password=old_password):
            raise serializers.ValidationError("Old password is incorrect")

        user.set_password(password)
        user.save()
        return attrs


class SendResetPasswordEmailViewSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)

    class Meta:
        fields = ['email']

    def validate(self, attrs):
        print(attrs, '<<<<<<<atters is here')
        email = attrs.get('email')
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.id))
            print('encoded uid', uid)
            token = PasswordResetTokenGenerator().make_token(user)
            print('password Reset Token', token)
            link = 'http://localhost:8080/api/user/reset/'+uid+'/'+token
            print('Password reset link', link)
            # Send Email
            return attrs

        else:
            raise ValidationError('you are Registered User')


class UserPasswordResetSerializer(serializers.Serializer):
    password = serializers.CharField(
        max_length=255, style={'input_type': 'password'}, write_only=True)
    password2 = serializers.CharField(
        max_length=255, style={'input_type': 'password'}, write_only=True)

    class Meta:
        fields = ['password', 'password2']

    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        # user = self.context.get('user')
        uid = self.context.get('uid')
        token = self.context.get('token')
        if password != password2:
            raise serializers.ValidationError(
                "password and conform Password doesn't match")
        id = smart_str(urlsafe_base64_decode(uid))
        user = User.objects.get(id=id)
        if not PasswordResetTokenGenerator().check_token(user, token):
            raise ValidationError('Token is not valid or exprired.')
        user.set_password(password)
        user.save()
        return attrs
