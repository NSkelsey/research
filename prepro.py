import os
import zipfile
import glob
import re
import string
import datetime

regex =  r"[0-9]+\|[0-9]+\|[^\|]?\|\d*\|(?P<data>\d*/\d*/\d*)?\|[^\r\n]*\r\n"

base = "LOAD DATA INFILE 'PATH' INTO TABLE $ FIELDS TERMINATED BY '|' LINES TERMINATED BY '\r\n';"

def process_file(filename, regex):
    fin = open(filename)
    expr = regex
    fout = open(filename+".out", 'w')
    s = fin.read()
    def replace(matcho):
        if matcho.group(1) == "" or matcho.group(1) is None:
            return matcho.group(0)
        else:
            return string.replace(matcho.group(0), matcho.group(1), datetime.datetime.strptime(matcho.group(1), "%m/%d/%Y").strftime("%Y-%m-%d"))
    s = re.subn(expr, replace, s)
    fout.write(s[0])
    print filename, " replacements: ", s[1]
    fout.close()
    fin.close()

def unzip_dir(directory):
    os.chdir(directory)
    gl = glob.glob('./*.zip')
    for entry in gl:
        zipf = zipfile.ZipFile(entry)
        print zipf.namelist()
        zipf.extractall()
    ul = glob.glob('./*.txt')
    return ul




def make_mysql_statment(cpath, tablename):
    os.chdir(cpath)
    print os.getcwd()
    gl = glob.glob('*.out')
    if len(gl) == 0:
        gl = glob.glob('*.txt')
    print gl
    for i in range(len(gl)):
        gl[i] = os.getcwd() + "/" + gl[i]
    li = []
    for i in range(len(gl)):
        temp = string.replace(base, "$", tablename)
        li.append(string.replace(temp, "PATH", gl[i]))
    f = open("load_data.sql", "w")
    for i in li:
        f.write(i)

    f.close()

def conv_date(s):
    return datetime.datetime.strptime(s, "%m/%d/%Y").strftime("%Y-%m-%d")

def unzip_and_process(dd):
    dirname = os.path.split(dd)[1]
    os.chdir(dd)
    gl = glob.glob('./*.zip')
    print gl
    for entry in gl:
        zipf = zipfile.ZipFile(entry)
        print zipf.namelist()
        zipf.extractall()
        filename = zipf.namelist()[0]
        fin = open(filename, 'r+')
        if (dirname ==  "foitext"):
            expr = r"[0-9]+\|[0-9]+\|[^\|]?\|\d*\|(?P<data>\d*/\d*/\d*)?\|[^\r\n]*\r\n"
            fout = open(filename+".out", 'w')
            s = fin.read()
            def replace(matcho):
                if matcho.group(1) == "" or matcho.group(1) is None:
                    return matcho.group(0)
                else:
                    return string.replace(matcho.group(0), matcho.group(1), datetime.datetime.strptime(matcho.group(1), "%m/%d/%Y").strftime("%Y-%m-%d"))
            s = re.subn(expr, replace, s)
            fout.write(s[0])
            print filename, " replacements: ", s[1]
            fout.close()

        if (dirname == "mdrdataa"):
            expr = r'\d+\|\d+\|[^\|]*\|[^\|]*\|[^\|]*\|[^\|]*\|[^\|]*\|(?P<date_received>[^\|]*)\|[^\|]*\|[^\|]*\|(?P<date_report>[^\|]*)\|(?P<date_event>[^\|]*)\|[^\|]*\|[^\|]*\|[^\|]*\|[^\|]*\|[^\|]*\|[^\|]*\|[^\|]*\|[^\|]*\|[^\|]*\|[^\|]*\|[^\|]*\|[^\|]*\|[^\|]*\|(?P<report_date>[^\|]*)\|[^\|]*\|(?P<date_report_FDA>[^\|]*)\|[^\r\n]*\r\n'
            fout = open(filename+".out", 'w')
            def replace(matcho):
                ostring = matcho.group(0)
                for match in matcho.groups():
                    if match is None or match == "":
                        pass
                    else:
                        ostring = string.replace(ostring, match, conv_date(match))
                return ostring

            for line in fin:
                s = line
                s = re.sub(expr, replace, s)
                fout.write(s)
            print filename, " replacements: "
            fout.close()

#program assumes we start with data/ dir below us correctly populated with zipfile
if "__name__" == "__main__":
    root = os.path.join(os.getcwd(), "data")

    os.chdir(os.path.join(os.getcwd(), "data"))
    datadirs = os.listdir(os.getcwd())
    print datadirs
    for dd in datadirs:
        os.chdir(root)
        unzip_and_process(dd)



