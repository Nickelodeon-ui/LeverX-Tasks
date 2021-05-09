import string

class Version:
    # Evaluation of version hierarchy
    VERSION_ORDER = {"a": 0, "alpha": 0, "beta": 1, "b": 1, "rc": 2, "release candidate": 2, "r": 3, "release": 3}

    def __init__(self, version):
        self.version = version
    
    def prepare_char(self, v_char):
        if "-" in v_char:
            version_num = v_char[:v_char.index("-")]
            version_stage = v_char[v_char.index("-") + 1:]
            v_char = {"version_num": int(version_num), "version_stage": version_stage, "dash": True}
        elif all([char in string.digits for char in v_char]):
            version_num = v_char
            v_char = {"version_num": int(version_num), "version_stage": None, "dash": False}
        elif any([digit in v_char for digit in string.digits]):
            index = 0
            while v_char[index] in string.digits:
                index += 1
            char_start_index = index
            version_num = v_char[:char_start_index]
            version_stage = v_char[char_start_index:]
            v_char = {"version_num": int(version_num), "version_stage": version_stage, "dash": False, "dig-char": True}
        else:
            version_stage = v_char
            v_char = {"version_num": -1, "version_stage": version_stage, "dash": False}
        return v_char

    def __lt__(self, version_2):
        v_contains = self.version.split(".")
        v2_contains = version_2.version.split(".")

        for v_char, v2_char in zip(v_contains, v2_contains):
            try:
                v_char = int(v_char)
                v2_char = int(v2_char)
                if v_char < v2_char:
                    return True
            except ValueError:
                v_char = str(v_char)
                v2_char = str(v2_char)
                if v_char == v2_char:
                    continue
                
                v_char = self.prepare_char(v_char)
                v2_char = self.prepare_char(v2_char)

                if v_char["version_num"] < v2_char["version_num"]:
                    return True
                elif v_char["version_num"] > v2_char["version_num"]:
                    return False
                
                if v_char["dash"] and v2_char["dash"]:
                    if self.VERSION_ORDER.get(v_char["version_stage"]) < self.VERSION_ORDER.get(v2_char["version_stage"]):
                        return True
                    else: 
                        return False
                
                if v_char["version_num"] == -1 and v2_char["version_num"] == -1:
                    return True if self.VERSION_ORDER.get(v_char["version_stage"]) \
                        < self.VERSION_ORDER.get(v2_char["version_stage"]) else False

                if v_char["dash"] and not v2_char["dash"]:
                    return True
                elif not v_char["dash"] and v2_char["dash"]:
                    return False
            
                if "dig-char" in v_char.keys() and "dig-char" in v2_char.keys():
                    if v_char["version_stage"] < v2_char["version_stage"]:
                        return True
                    else:
                        return False

                if v_char["version_stage"] is None and v2_char["version_stage"]:
                    return True
                else:
                    return False
        else:
            return False

    def __gt__(self, version_2):
        v_contains = self.version.split(".")
        v2_contains = version_2.version.split(".")

        for v_char, v2_char in zip(v_contains, v2_contains):
            try:
                v_char = int(v_char)
                v2_char = int(v2_char)
                if v_char > v2_char:
                    return True
            except ValueError:
                v_char = str(v_char)
                v2_char = str(v2_char)
                if v_char == v2_char:
                    continue
                
                v_char = self.prepare_char(v_char)
                v2_char = self.prepare_char(v2_char)

                if v_char["version_num"] > v2_char["version_num"]:
                    return True
                elif v_char["version_num"] < v2_char["version_num"]:
                    return False
                
                if v_char["dash"] and v2_char["dash"]:
                    if self.VERSION_ORDER.get(v_char["version_stage"]) > self.VERSION_ORDER.get(v2_char["version_stage"]):
                        return True
                    else: 
                        return False
                
                if v_char["version_num"] == -1 and v2_char["version_num"] == -1:
                    return True if self.VERSION_ORDER.get(v_char["version_stage"]) \
                        > self.VERSION_ORDER.get(v2_char["version_stage"]) else False

                if not v_char["dash"] and v2_char["dash"]:
                    return True
                elif v_char["dash"] and not v2_char["dash"]:
                    return False
            
                if "dig-char" in v_char.keys() and "dig-char" in v2_char.keys():
                    if v_char["version_stage"] > v2_char["version_stage"]:
                        return True
                    else:
                        return False

                if v_char["version_stage"] and v2_char["version_stage"] is None:
                    return True
                else:
                    return False
        else:
            return False

    def __eq__(self, version_2):
        v_contains = self.version.split(".")
        v2_contains = version_2.version.split(".")
        for v_char, v2_char in zip(v_contains, v2_contains):
            if v_char != v2_char:
                return False
        else:
            return True
    
    def __ne__(self, version_2):
        v_contains = self.version.split(".")
        v2_contains = version_2.version.split(".")
        for v_char, v2_char in zip(v_contains, v2_contains):
            if v_char != v2_char:
                return True
        else:
            return False

def main():
    to_test = [
        ("1.0.0", "2.0.0"),
        ("1.0.0", "1.42.0"),
        ("1.2.0", "1.2.42"),
        ("1.1.0-alpha", "1.2.0-alpha.1"),
        ("1.0.1b", "1.0.10-alpha.beta"),
        ("1.0.0-rc.1", "1.0.0"),
        ("beta", "2-rc"),
    ]

    for version_1, version_2 in to_test:
        assert Version(version_1) < Version(version_2), "lt failed"
        assert Version(version_2) > Version(version_1), "gt failed"
        assert Version(version_2) != Version(version_1), "neq failed"
        
    print("Success!")

if __name__ == "__main__":
    main()
