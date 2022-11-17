class v:
    def __init__(self, major: int, minor: int, micro: int):
        self.ver = (major, minor, micro)
    
    def from_bytes(v_bytes: bytes):
        return v(v_bytes[0], v_bytes[1], v_bytes[2])

    def __str__(self):
        return f"{self.ver[0]}.{self.ver[1]}.{self.ver[2]}"

    def __bytes__(self):
        return self.ver[0].to_bytes(1,'big')+self.ver[1].to_bytes(1,'big')+self.ver[2].to_bytes(1,'big')

    def __iter__(self):
        return iter(self.ver)

    def __eq__(self, eq):
        if(isinstance(eq, v)): return self.ver==eq.ver
        return type(eq)(self.ver)==eq
    
    def is_compatible_with(self, ver):
        for i in version_compatibility_table:
            if(self.ver in i and ver in i):
                return True
        else:
            return False


nrep_version = v(0,1,2)

version_compatibility_table = (
    (v(0,1,0)),
    (v(0,1,1), v(0,1,2))
)