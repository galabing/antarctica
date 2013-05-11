#!/usr/bin/python2.7

""" Generates price curves from arbitrageur log.
"""

import argparse
import re

# Eg, [INFO] 2013-05-08 12:03:33,430 Opportunity: buy=109.77 sell=113.06 from=BTC-E to=Bitstamp amount=32.46127753 pay=3563.22 paid=3670.14 profit=106.92 rate=3.00% mrate=2.01%
time_pattern = '\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}'
pattern = ('\[INFO\] (?P<time>%s) Opportunity: buy=(?P<buy>[\d.]+)'
           ' sell=(?P<sell>[\d.]+) from=(?P<from>[\w-]+) to=(?P<to>[\w-]+)'
           ' amount=(?P<amount>[\d.]+) pay=(?P<pay>[\d.]+)'
           ' paid=(?P<paid>[\d.]+) profit=(?P<profit>[\d.]+)'
           ' rate=(?P<rate>[\d.]+)%% mrate=(?P<mrate>[\d.]+)%%') % time_pattern

def process(log_file, html_file):
  prog = re.compile(pattern)
  curves = dict()
  with open(log_file, 'r') as fp:
    while True:
      line = fp.readline()
      if line == '':
        break
      result = prog.match(line[:-1])
      if result is None:
        continue
      time = result.group('time')
      source = result.group('from')
      destination = result.group('to')
      buy = float(result.group('buy'))
      sell = float(result.group('sell'))
      profit = float(result.group('profit'))
      key = '%s:%s' % (source, destination)
      if key not in curves:
        curves[key] = [[time[5:-7], buy, sell, profit]]
      else:
        curves[key].append([time[5:-7], buy, sell, profit])
  with open(html_file, 'w') as fp:
    html_lines = []
    print >> fp, '<html>'
    print >> fp, '  <head>'
    print >> fp, '    <script type="text/javascript"'
    print >> fp, '            src="https://www.google.com/jsapi">'
    print >> fp, '    </script>'
    print >> fp, '    <script type="text/javascript">'
    print >> fp, '      google.load("visualization", "1",'
    print >> fp, '                  {packages:["corechart"]});'
    print >> fp, '      google.setOnLoadCallback(drawChart);'
    print >> fp, '      function drawChart() {'
    for key, data in curves.iteritems():
      source, destination = key.split(':')
      var_prefix = '%s_%s' % (source.replace('-', '_'),
                              destination.replace('-', '_'))
      data_var = '%s_data' % var_prefix
      options_var = '%s_options' % var_prefix
      chart_var = '%s_chart' % var_prefix
      chart_div = '%s_div' % var_prefix
      # Prints a curve entry to JS code, eg:
      # var data = google.visualization.arrayToDataTable([
      #          ['Year', 'Sales', 'Expenses'],
      #          ['2004',  1000,      400],
      #          ['2005',  1170,      460],
      #          ['2006',  660,       1120],
      #          ['2007',  1030,      540]
      #        ]);
      fp.write('var %s = google.visualization.arrayToDataTable([\n'
               '  ["time", "%s", "%s", "profit"]' %
               (data_var, source, destination))
      for row in data:
        fp.write(',\n    ["%s", %f, %f, %f]' %
                 (row[0], row[1], row[2], row[3]))
      fp.write(']);\n')
      print >> fp, 'var %s = { title: "buy %s, sell %s" }' % (
          options_var, source, destination)
      print >> fp, ('var %s = new google.visualization.LineChart('
             'document.getElementById("%s"));' % (chart_var, chart_div))
      print >> fp, '%s.draw(%s, %s);' % (chart_var, data_var, options_var)
      html_lines.append('<div id="%s" style="width: 1600px; height: 800px;">'
                        '</div>' % chart_div)
    print >> fp, '      }'
    print >> fp, '    </script>'
    print >> fp, '  </head>'
    print >> fp, '  <body>'
    for line in html_lines:
      print >> fp, line
    print >> fp, '  </body>'
    print >> fp, '</html>'

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--log_file', required=True)
  parser.add_argument('--html_file', required=True)
  args = parser.parse_args()
  process(args.log_file, args.html_file)

if __name__ == '__main__':
  main()

