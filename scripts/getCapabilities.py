''' gets and stores the capabilities documents for the given services'''
import json, urllib2, logging as LOG, datetime, os, argparse
import lxml.etree as etree

__timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S')

def _getAndStoreDocument(url, directory, filename):
    '''
	Gets and stores document from a url to directory with filename.
	The stored document is pretty-printed.
	
	@param url: url to retrieve
	@type url: String
	@param directory: directory to store file
	@type directory: String
	@param filename: name of the file to store
    @type filename: String 
	'''
    try:
        content = urllib2.urlopen(url)
        LOG.info("retrieving url: " + url + ", status: " + str(content.getcode())) 
        
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        with open(directory + filename, 'w') as fp:
            while True:
                chunk = content.read(16 * 1024)
                if not chunk: break
                fp.write(chunk)
        
        # pretty print all responses
        parser = etree.XMLParser(remove_blank_text=True)
        tree = etree.parse(directory + filename, parser)
        tree.write(directory + filename, pretty_print=True)
        
    except urllib2.HTTPError , error:
        LOG.error("Error retrieving url: " + url + ", status: " + str(error.code)) 
    
if __name__ == "__main__":
    ''' main macro '''
    parser = argparse.ArgumentParser(description='Parsing parameters....')
    parser.add_argument('-X', '--debug', help='enable DEBUG logging',
                        action="store_true", required=False)
    args = parser.parse_args()

    if (args.debug):
        LOG.basicConfig(level=LOG.DEBUG,
                format='%(asctime)s - %(levelname)-7s %(module)s::%(lineno)d: %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='../logs/' + __timestamp + '.log',
                filemode='w')
    else:
        LOG.basicConfig(level=LOG.INFO,
                format='%(asctime)s - %(levelname)-7s: %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='../logs/' + __timestamp + '.log',
                filemode='w')    
        
    # open and parse the json configuration
    f = open('../services.json')
    data = json.load(f)
    services = data['services']
    for service in services:
        LOG.debug("service found: " + str(service))
        # types is a list of dict
        types = service['types'][0]
        for sType in types:
            versions = types[sType]
            for version in versions:
                sUrl = service['url'] + '/' + sType + '?VERSION=' + version + '&REQUEST=GetCapabilities'
                sDir = '../services/dataset/' + service['name'] + '/' + sType + '/'
                sPath = 'capabilities_' + version + '.xml'
                _getAndStoreDocument(sUrl, sDir, sPath)
