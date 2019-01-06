from noke import error
from noke import nobject


class Cutter:
    def __init__(self, file: str):
        source = ""
        try:
            source = open(file, 'r').read()
        except:
            err = error.Error(3)
            err.launch()
        noke_obj = []
        objs = source.split("\n\n")
        for obj in objs:
            obj = obj.replace("\n", "").replace("\t", "").replace(
                "    ", "").replace("        ", "")
            print(obj)
            noke_obj.append(nobject.NObject(obj))
