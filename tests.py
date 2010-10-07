import unittest

from mongodm.document import Document, EmbeddedDocument
from mongodm.fields import StringField, ListField, EmbeddedDocumentField
from mongodm.fields import EmailField, IntegerField, DecimalField, ReferenceField
from mongodm.validators import ValidationError, Required, Unique
from mongodm.ext.wtf import MongodmForm
from mongodm.connection import Connection
from mongodm.ext.tree import TreeDocument

import wtforms

connection = Connection('localhost', 27017)
db = connection['test-database']

class User(EmbeddedDocument):
    first_name = StringField()
    last_name = StringField()

class Comment(EmbeddedDocument):
    author = StringField()
    message = StringField()
    replies = ListField('Comment')

class Post(Document):
    __collection__ = 'posts'
    __db__ = db
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
        Post.collection().insert(post)
        #retrieving
        document = Post.collection().find_one()

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
        Post.collection().insert(postbacked)
        assert post._id == postbacked._id #check if it was an update

    def testReferenceField(self):

        class A(Document):
            __collection__ = 'as'
            __db__ = db
            label = StringField()
            b = ReferenceField('B')

        class B(Document):
            __collection__ = 'bs'
            __db__ = db
            label = StringField()
            a = ReferenceField(A)

        A.collection().remove()
        B.collection().remove()

        a = A()
        a.label = 'i\'m a A'
        A.collection().insert(a)

        b = B()
        b.label = 'i\'m a B'
        B.collection().insert(b)
        
        a.b = b
        A.collection().save(a)
        
        assert a.b._id == b.id

        backed = A.collection().find_one()

        backed = backed.to(A)

        assert backed.b.label == 'i\'m a B'
        assert backed.b.id == b.id

        A.collection().remove()
        B.collection().remove()

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
        class Author(Document):
            """
            email has to be unic on a specific db
            """
            __collection__ = "authors"
            __db__ = db
            email_address = EmailField(validators=[Required(), Unique()])

        author = Author()
        author.email_address = 'titi@titi.com'
        Author.collection().insert(author)

        author = Author()
        author.email_address = 'titi@titi.com'
        self.assertRaises(ValidationError, author._to_dict)
        Author.collection().remove()

    def testIntegerField(self):
        class Test(Document):
            __collection__ = 'tests'
            __db__ = db
            integer = IntegerField()

        test = Test()
        test.integer = 12
        assert test.integer == 12
        Test.collection().insert(test)
        test_backed = Test.collection().find_one()
        test_backed = test_backed.to(Test)
        assert test_backed.integer == 12
        test_backed.integer += 1
        assert test_backed.integer == 13
        test_backed.integer = 'test'
        self.assertRaises(ValidationError, test_backed._to_dict)
        test_backed.integer = 12.5
        self.assertRaises(ValidationError, test_backed._to_dict)
        Test.collection().remove()

    def testDecimalField(self):
        class Test(Document):
            __collection__ = 'tests'
            __db__ = db
            decimal = DecimalField()

        test = Test()
        test.decimal = 12.5
        assert test.decimal == 12.5
        Test.collection().insert(test)
        test_backed = Test.collection().find_one()
        test_backed = test_backed.to(Test)
        assert test_backed.decimal == 12.5
        test_backed.decimal += 1
        assert test_backed.decimal == 13.5
        test_backed.decimal = 'test'
        self.assertRaises(ValidationError, test_backed._to_dict)
        Test.collection().remove()

    def testDocumentTree(self):

        class TreeNode(TreeDocument):
            __collection__ = 'nodes'
            __db__ = db
            label = StringField()
            parent = ReferenceField('TreeNode')

        root_node = TreeNode()
        root_node.label = 'root'
        TreeNode.collection().insert(root_node)

        first_child = TreeNode()
        first_child.label = 'first_child'
        first_child.parent = root_node
        TreeNode.collection().insert(first_child)

        second_child = TreeNode()
        second_child.label = 'first_child'
        second_child.parent = first_child
        TreeNode.collection().insert(second_child)

        third_child = TreeNode()
        third_child.label = 'third_child'
        third_child.parent = first_child
        TreeNode.collection().insert(third_child)

        assert root_node.children.count() == 3
        assert first_child.children.count() == 2
        assert second_child.children.count() == 0
        assert third_child.children.count() == 0
        assert root_node.level == 0
        assert first_child.level == 1
        assert second_child.level == 2
        assert third_child.level == 2

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
            __db__ = db
            email_address = EmailField()

        class AuthorForm(MongodmForm):
            __forclass__ = Author
            email_address = wtforms.TextField('Email Address')

        author = Author()
        author.email_address = 'some@bo.dy'
        #persists
        Author.collection().insert(author)
        assert author._id != None
        form = AuthorForm(obj=author)
        assert form.data['id'] == author._id
        assert form.data['id'] == author.id
        assert form.data['email_address'] == author.email_address
        Author.collection().remove() #cleaning up db

    def testWTFormsPopulateObject(self):
        class Author(Document):
            __collection__ = 'authors'
            email_address = EmailField()

        class AuthorForm(MongodmForm):
            __forclass__ = Author
            email_address = wtforms.TextField('Email Address')
        
    def testUp(self):
        pass

    def tearDown(self):
        Post.collection().remove()

if __name__ == '__main__':
    unittest.main()