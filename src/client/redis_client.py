import redis

redis_client = redis.Redis(host="localhost", port=6379, db=0)

# 打印key的个数
print(redis_client.dbsize())

# 读取key
redis_client.set("foo", "bar")
v = redis_client.get("foo")
sv = v.decode("utf-8")
print(v)
print(sv)

import datetime
from redis_om import HashModel
from typing import Optional


class Customer(HashModel):
    first_name: str
    last_name: str
    email: str
    join_date: datetime.date
    age: int
    bio: Optional[str]


andrew = Customer(
    first_name="Andrew",
    last_name="Brookins",
    email="andrew.brookins@example.com",
    join_date=datetime.date.today(),
    age=38,
)

do = andrew.save()
print(do)

do_key = do.key()
print(do_key)

read_obj = Customer.get(do.pk)
print(read_obj)
