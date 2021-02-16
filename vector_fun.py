import re
import log
import math
import plt_icon

logger = log.get_logger(__name__)



def calc_angel_3D(text):
    vectors = trans(text)
    logger.info(str(vectors))
    denominator, x, y, z = 1, 1, 1, 1
    vec = []
    for vector in vectors.values():
        x *= vector[0]
        y *= vector[1]
        z *= vector[2]
        denominator *= math.sqrt(sum(map(lambda x: x*x, vector)))
        vec.append(list(vector))
    numerators = sum([x, y, z])
    cos_f = numerators/denominator
    angle = math.degrees(math.acos(cos_f))
    logger.info(angle)
    file_name = plt_icon.get_vector(vec[0], vec[1])
    return angle, file_name
    pass


def trans(text: str) -> {str: tuple}:
    """
    Переводить текст 'a=(1,3,54) b=(1,4,6)' в список {'a': (1, 3, 54), 'b': (1,4,6)} для работы с векторами
    :param text: Векторы или точки
    :return:
    """
    d = {}
    list_of_text = re.findall('\w+', text)
    assert len(list_of_text) == 8, 'Где-то ошибка'
    logger.info(list_of_text)
    for i in [0, 4]:
        a = []
        for j in [1, 2, 3]:
             a.append(int(float(list_of_text[i+j])))
        d[list_of_text[i]] = tuple(a)
    return d

