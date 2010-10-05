import unittest

from mongodm.document import Document, EmbeddedDocument
from mongodm.fields import StringField, ListField, EmbeddedDocumentField
from mongodm.fields import EmailField, IntegerField, DecimalField, ReferenceField
from mongodm.validators import ValidationError, Required, Unique
from mongodm.ext.wtf import MongodmForm
from mongodm.connection import Connection
import wtforms


class User(EmbeddedDocument):
    first_name = StringField()
    last_name = StringField()

class Comment(EmbeddedDocument):
    author = StringField()
    message = StringField()
    replies = ListField('Comment')

class Post(Document):
    __collection__ = 'posts'
    title = StringField()
    content = StringField()
    comments = ListField(Comment)
    created_by = EmbeddedDocumentField('User')

class DocumentTest(unittest.TestCase):

    def testSimpleDocument(self):
        post = Post()
        assert len(post._fields)==4
        assert issubclass(post.__class__, Document)
        post.title = 'first post title'
        post.content = 'first post content'
        assert post.title == 'first post title'
        assert post.content == 'first post content'

    def testEmbeddedDocument(self):
        post = Post()
        user = User()
        user.first_name = 'paul'
        user.last_name = 'dupont'
        post.created_by = user
        assert post.created_by.first_name=='paul'
        assert post.created_by.last_name=='dupont'
        user.first_name = 'jean'
        assert post.created_by.first_name=='jean'

    def testListField(self):
        post = Post()
        post.title = 'first post title'
        post.content = 'first post content'
        user = User()
        user.first_name = 'paul'
        user.last_name = 'dupont'
        post.created_by = user
        comment = Comment()
        comment.author = 'jean-philippe'
        comment.message = 'my message'
        post.comments.append(comment)
        assert post._to_dict() == {
            'content': 'first post content',
            'comments': [
                {'message': 'my message',
                'author': 'jean-philippe', 'replies': []}
            ], 'created_by': {'first_name': 'paul', 'last_name': 'dupont'},
            'title': 'first post title'}
        reply = Comment()
        reply.author = 'jean-philippe'
        reply.message = 'reply to my message'
        comment.replies.append(reply)
        assert post.comments[0].replies[0].message == 'reply to my message'
        assert post.comments[0].replies[0].author == 'jean-philippe'

        #persists
        db = self.get_db()
        Post.collection(db).insert(post)
        #retrieving
        document = Post.collection(db).find_one()
        assert document.__class__.__name__ == 'MongoDocument'
        assert document._id == post._id
        assert document.comments[0].replies[0].message == 'reply to my message'
        assert document.comments[0].replies[0].author == 'jean-philippe'
        postbacked = document.to(Post)
        assert postbacked.__class__ == Post
        assert postbacked.created_by.__class__ == User
        assert postbacked.created_by.first_name == 'paul'
        assert postbacked.created_by.last_name == 'dupont'
        assert postbacked.comments[0].replies[0].__class__ == Comment
        assert postbacked.comments[0].replies[0].message == 'reply to my message'
        assert postbacked.comments[0].replies[0].author == 'jean-philippe'
        assert post._id == postbacked._id
        Post.collection(db).insert(postbacked)
        assert post._id == postbacked._id #check if it was an update

    def testReferenceField(self):

        db = self.get_db()

        class A(Document):
            __collection__ = 'as'
            label = StringField()
            b = ReferenceField('B', db)

        class B(Document):
            __collection__ = 'bs'
            label = StringField()
            a = ReferenceField(A, db)


        a = A()
        a.label = 'i\'m a A'
        A.collection(db).insert(a)

        b = B()
        b.label = 'i\'m a B'
        B.collection(db).insert(b)
        
        a.b = b
        A.collection(db).save(a)
        
        assert a.b._id == b.id

        backed = A.collection(db).find_one()
        
        A.collection(db).remove()
        B.collection(db).remove()

    def testEmailValidator(self):
        class Author(Document):
            email_address = EmailField()
        author = Author()
        self.assertRaises(ValidationError, author._fields['email_address']._validators[0], 'foo')
        self.assertRaises(ValidationError, author._fields['email_address']._validators[0], 'foo.bar')
        author.email_address = 'foo'
        self.assertRaises(ValidationError, author._to_dict)
        author.email_address = 'foo.bar'
        self.assertRaises(ValidationError, author._to_dict)
        
    def testRequiredValidator(self):
        class Author(Document):
            email_address = EmailField(validators=[Required()])
        author = Author()
        self.assertRaises(ValidationError, author._fields['email_address']._validators[0], '')
        author.email_address = ''
        self.assertRaises(ValidationError, author._to_dict)

    def testUniqueValidator(self):
        db = self.get_db()
        class Author(Document):
            __collection__ = "authors"
            """
            email has to be unic on a specific db
            """
            email_address = EmailField(validators=[Required(), Unique(db)])

        author = Author()
        author.email_address = 'titi@titi.com'
        Author.collection(db).insert(author)

        author = Author()
        author.email_address = 'titi@titi.com'
        self.assertRaises(ValidationError, author._to_dict)
        Author.collection(db).remove()

    def testIntegerField(self):
        class Test(Document):
            __collection__ = 'tests'
            integer = IntegerField()
        test = Test()
        test.integer = 12
        assert test.integer == 12
        db = self.get_db()
        Test.collection(db).insert(test)
        test_backed = Test.collection(db).find_one()
        test_backed = test_backed.to(Test)
        assert test_backed.integer == 12
        test_backed.integer += 1
        assert test_backed.integer == 13
        test_backed.integer = 'test'
        self.assertRaises(ValidationError, test_backed._to_dict)
        test_backed.integer = 12.5
        self.assertRaises(ValidationError, test_backed._to_dict)
        Test.collection(db).remove()

    def testDecimalField(self):
        class Test(Document):
            __collection__ = 'tests'
            decimal = DecimalField()
        test = Test()
        test.decimal = 12.5
        assert test.decimal == 12.5
        db = self.get_db()
        Test.collection(db).insert(test)
        test_backed = Test.collection(db).find_one()
        test_backed = test_backed.to(Test)
        assert test_backed.decimal == 12.5
        test_backed.decimal += 1
        assert test_backed.decimal == 13.5
        test_backed.decimal = 'test'
        self.assertRaises(ValidationError, test_backed._to_dict)
        Test.collection(db).remove()

    def testWTFormsSharedValidation(self):
        class Author(Document):
            email_address = EmailField()

        class AuthorForm(MongodmForm):
            __forclass__ = Author
            email_address = wtforms.TextField('Email Address')

        form = AuthorForm()
        form.process(email_address = 'toto')
        assert form.data == {'id': None, 'email_address' : 'toto'} #wtforms ok
        form.validate()
        assert form.errors != {} #MongodmForm ok
        assert form.errors == {'email_address': [u'Invalid email address.']}

    def testWTFormsFromObject(self):
        class Author(Document):
            __collection__ = 'authors'
            email_address = EmailField()

        class AuthorForm(MongodmForm):
            __forclass__ = Author
            email_address = wtforms.TextField('Email Address')

        author = Author()
        author.email_address = 'some@bo.dy'
        #persists
        db = self.get_db()
        Author.collection(db).insert(author)
        assert author._id != None
        form = AuthorForm(obj=author)
        assert form.data['id'] == author._id
        assert form.data['id'] == author.id
        assert form.data['email_address'] == author.email_address
        Author.collection(db).remove() #cleaning up db

    def testWTFormsPopulateObject(self):
        class Author(Document):
            __collection__ = 'authors'
            email_address = EmailField()

        class AuthorForm(MongodmForm):
            __forclass__ = Author
            email_address = wtforms.TextField('Email Address')
        
    def testUp(self):
        pass

    def get_db(self):
        connection = Connection('localhost', 27017)
        return connection['test-database']

    def tearDown(self):
        Post.collection(self.get_db()).remove()

if __name__ == '__main__':
    unittest.main()