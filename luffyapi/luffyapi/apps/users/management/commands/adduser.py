from django.core.management.base import BaseCommand, CommandError
from faker import Faker
from django.contrib.auth.hashers import make_password

from ...models import User


class Command(BaseCommand):
    help = "批量创建新用户"
    def add_arguments(self, parser):

        parser.add_argument(
            '--num',
            nargs='+',
            type=int,
            action='store',
            default='close',
            help='用户',
        )

    def handle(self, *args, **options):
        faker = Faker(locale='zh_CN')
        password = 123456
        # try:
        #     if options['num']:
        #         print('hello world, %s' % options['num'][0])
        #
        #     self.stdout.write(self.style.SUCCESS('命令%s执行成功, 参数为%s' % (__file__, options['num'])))
        # except Exception:
        #     self.stdout.write(self.style.ERROR('命令执行出错'))

        for i in range(options['num'][0]):
            data = {}
            data['username'] = faker.name_male()
            data['phone'] = faker.phone_number()
            data['password'] = make_password(password)
            try:
                User.objects.create(**data)
                user = User.objects.all()
                print(user[i].username,user[i].phone,user[i].password)
                # print(i)
            except Exception:
                raise CommandError('%s用户名存在,请重试'% (faker.name_male()))


