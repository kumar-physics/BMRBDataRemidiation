import pynmrstar
import json
from urllib.request import urlopen, Request
import re

class CheckEntries(object):

    def __init__(self,bmrb_id):
        #self.get_data_from_restraints_grid(bmrb_id)
        #star_data = self.get_data(bmrb_id)
        #print (star_data)
        #self.get_data_test(bmrb_id)
        #self.check_peak_set_id()
        self.check_peak_list(bmrb_id)


    @staticmethod
    def get_tag_data(entry_id,loop_category):
        #url = 'http://rest.bmrb.wisc.edu/bmrb/NMR-STAR3/{}'.format(entry_id)
        #print (url)
        star_data = pynmrstar.Entry.from_database(entry_id)
        loop_data = star_data.get_tag('{}.Text_data'.format(loop_category))
        return loop_data

    def check_peak_list(self,entry_id):
        star_data = pynmrstar.Entry.from_database(entry_id)
        sf_data = star_data.get_saveframes_by_category('spectral_peak_list')
        list_id = 1
        for sf in sf_data:
            format = sf.get_tag('_Spectral_peak_list.Text_data_format')
            data = sf.get_tag('_Spectral_peak_list.Text_data')[0]
            dim = int(sf.get_tag('_Spectral_peak_list.Number_of_spectral_dimensions')[0])
            #parsed_data = re.findall(r'\s+(\S+)\s*(\S+)\s*(\S+)\s*(\S+)\s+\n',data)
            #parsed_data = re.findall(r'\s*(\d+.\d+)\s*(\d+.\d+)\s*(\d+.\d+)\s*(\d+)\s*\n',data)#11017
            #parsed_data = re.findall(r'\s*\S+\s*(\S+)\s*(\S+)\s*1\s*U\s*(\S+)\s+0\s*e\s*0\s*\d+\s*\d+\s*\n', data)  # 15025
            if dim == 2:
                parsed_data = re.findall(r'\s+\d+\s+(\S+)\s+(\S+)\s* 1 \s* ? \s*(\S+)\s+\S+\s+ e \s+0\s+\S+\s+\S+\s+0\s*\n',data)
            elif dim == 3:
                parsed_data = re.findall(r'\s*\S+\s*(\S+)\s*(\S+)\s*(\S+)\s+1\s+\S+\s+(\S+)\s+\S+\s+e\s+0\s+\S+\s+\S+\s+\S+\s+0\s*\n',data) # 15074
            else:
                print ("Dim error")
            parsed_data = re.findall(r'\s*\S+\s*(\S+)\s*(\S+)\s*(\S+)\s*1\s*?\s*(\S+)\s*\S+\s*e\s*0\s*\S*\s*\S*\s*\S*\s*0\s*\n', data)  # 15074
            print (parsed_data)
            peak_dict = {}
            id = 1
            for p in parsed_data:
                peak_dict[id] =p
                id+=1
            lp = self.generate_peak_general_char_loop(peak_dict,int(dim),'height',list_id,entry_id)
            sf.add_loop(lp)
            lp2 = self.generate_peak_char_loop(peak_dict,int(dim),list_id,entry_id)
            sf.add_loop(lp2)
            sf.add_tag('_Spectral_peak_list.Text_data','.',update=True)
            list_id+=1
        star_data.normalize()
        with open('{}.str'.format(entry_id),'w') as outfile:
            outfile.write(str(star_data))


    def generate_peak_general_char_loop(self,peak_data,dim,method,list_id,entry_id):
        lp = pynmrstar.Loop.from_template('_Peak_general_char')
        for k in peak_data.keys():
            lp.add_data([k, peak_data[k][dim], '.',method, entry_id, list_id])
        return lp

    def generate_peak_char_loop(self,peak_data,dim,list_id,entry_id):
        lp2 = pynmrstar.Loop.from_template('_Peak_char')
        for k in peak_data.keys():
            for i in range(1, dim+1):
                lp2.add_data(
                    [k, i, peak_data[k][i - 1], '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.',
                     entry_id, list_id])
        return lp2

    def check_peak_set_id(self):
        url = Request("http://webapi.bmrb.wisc.edu/v2/list_entries?database=macromolecules")
        url.add_header('Application', 'Kumaran')
        r = urlopen(url)
        dump = json.loads(r.read())
        for bmrb_id in dump:
            self.check_peak_list(bmrb_id)


            # #print ('Checking entry {}'.format(bmrb_id))
            # star_data = pynmrstar.Entry.from_database(bmrb_id)
            # loop_data = star_data.get_loops_by_category('_Assigned_peak_chem_shift')
            # for lp in loop_data:
            #     col_names = lp.get_tag_names()
            #     pk_id = col_names.index('_Assigned_peak_chem_shift.Peak_ID')
            #     dim_id = col_names.index('_Assigned_peak_chem_shift.Spectral_dim_ID')
            #     set_id = col_names.index('_Assigned_peak_chem_shift.Set_ID')
            #     list_id = col_names.index('_Assigned_peak_chem_shift.Spectral_peak_list_ID')
            #     chk = True
            #     for dat in lp.data:
            #         try:
            #             sid = int(dat[set_id])
            #         except ValueError:
            #             if chk:
            #                 print (bmrb_id,dat[list_id])
            #                 chk = False

    def get_data_from_restraints_grid(self,entry_id):
        url = 'http://www.bmrb.wisc.edu/ftp/pub/bmrb/nmr_pdb_integrated_data/coordinates_restraints_chemshifts/all/' \
              'nmr-star/{}/{}_linked.str'.format(entry_id.lower(),entry_id.lower())
        #url = 'http://rest.bmrb.wisc.edu/bmrb/NMR-STAR3/{}'.format(entry_id)
        star_data = pynmrstar.Entry.from_file(url)
        print (url)
        print (star_data)






if __name__=="__main__":
    p = CheckEntries('15074')
    #p.check_peak_set_id()