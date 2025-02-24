from app.utils.exception import RandomException


async def random_function2():
    return 10


async def random_function():
    if await random_function2() > 5:
        return True
    raise RandomException("Number is less than 5")
