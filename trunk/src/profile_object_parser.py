from hotshot import stats
import sys

s = stats.load('data.prof')

def usage(s):
    d = s.get_sort_arg_defs()
    print "Run application with 'twistd -noy <app.tac> --profile=data.prof --savestats'"
    print "The to analyze output (saved in data.prof) you should run"
    print "python profile_object_parser.py parameter [num]" 
    print "=-" * 30
    
    for item in d.iteritems():
        print '* ', item[0], '--->', item[1][1]

try:
    if len(sys.argv) < 2:
        usage(s)
        raise Exception("Invalid sorting parameter")
    elif len(sys.argv) == 2:
        sortby = sys.argv[1]
        num = 30
    elif len(sys.argv) == 3:
        sortby = sys.argv[1]
        num = int(sys.argv[2])

    s.sort_stats(sortby)
    s.print_stats(num)
except:
    usage(s)