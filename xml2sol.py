import xml.dom.minidom
import sys

solution = xml.dom.minidom.parse(sys.stdin)
variables = solution.getElementsByTagName('variable')

print('TakenDealId')
deal_prefix = 'Deal_'
for variable in variables:
    if variable.attributes['name'].nodeValue.startswith(deal_prefix) and variable.attributes['value'].nodeValue == '1':
        taken_deal = variable.attributes['name'].nodeValue
        taken_deal_id = int(taken_deal[len(deal_prefix):])
        print(taken_deal_id)
