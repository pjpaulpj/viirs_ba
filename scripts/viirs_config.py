"""Configuration abstraction for the VIIRS BA code

The VIIRS BA code needs to be run standalone as well as under
the control of an optimization algorithm such as those implemented
in scipy.optimize. This means that the configuration needs to be 
represented sometimes as an INI file and sometimes as a vector of 
parameters, where the value at each index of the vector has a specific
meaning. And, of course, there needs to be a way to translate back and 
forth between equivalent representations of the same configuration.

More correctly, a subset of the INI configuration must be expressible as 
a vector of consistently interpreted parameters. The remaining parameters
control various program features, such as the formats in which to store outputs, 
working directory, filenames for various inputs and outputs, etc.

In essense, the [Thresholds] and [ConfirmBurnParameters] section of the INI 
file must be representable as a vector of values, while the other sections may vary.
"""
from collections import namedtuple
from ConfigParser import ConfigParser
import glob
import os.path
import re


float_vector_params = ['M07UB', 'M08LB', 'M08UB', 
                      'M10LB', 'M10UB', 'M11LB', 
                      'RthSub', 'Rth', 'RthLB', 'MaxSolZen']                      
int_vector_params = ['TemporalProximity', 'SpatialProximity']
vector_param_names = float_vector_params + int_vector_params

ConfigVector = namedtuple('ConfigVector', vector_param_names )
                  
class VIIRSConfig (object) : 
    @classmethod
    def merge_into_template(cls, thresh_vec, template) : 
        """creates a new VIIRSConfig object with thresh_vec grafted into the template
        
        Values in the resultant object may be "perturbed" in order to 
        produce a unique schema and/or directory name for the outputs."""
        #create a new object
        merged = cls()
        
        # copy the fixed values
        merged.TextOut       = template.TextOut
        merged.ShapeOut      = template.ShapeOut
        merged.DatabaseOut   = template.DatabaseOut
        merged.PostBin       = template.PostBin
        
        merged.DBname        = template.DBname
        merged.DBuser        = template.DBuser
        merged.DBschema      = template.DBschema
        merged.DBhost        = template.DBhost
        merged.pwd           = template.pwd
        
        merged.ImageDates    = template.ImageDates
        merged.BaseDir       = template.BaseDir
        merged.use375af      = template.use375af
        merged.use750af      = template.use750af
        
        # merge in the vector data
        for p in vector_param_names : 
            setattr(merged, p, getattr(thresh_vec, p))        

        # merge in the geographic window if present
        if template.has_window() : 
            merged.north = template.north 
            merged.south = template.south
            merged.east  = template.east
            merged.west  = template.west

        # handle changes
        merged.run_id      = cls.create_run_id(merged)
        merged.ShapePath = merged.perturb_dir(template.ShapePath)
        merged.perturb_schema() 
        merged.sort_dates()
        
        
        return merged

    @classmethod
    def load_batch(cls, base_dir) : 
        """explores all subdirectories of base_dir for ini_files, loads
        them, and returns them as a list."""
        ini_files = glob.glob('{0}/*/*.ini'.format(base_dir))
        config_list = [cls.load(i) for i in ini_files ]
        return config_list

        
    @classmethod
    def load(cls, filename) : 
        """Loads an ini file and creates a configuration object"""
        ini = ConfigParser() 
        ini.read(filename)
        # copy the fixed values
        
        target = cls()
        target.BaseDir = ini.get("InDirectory", "BaseDirectory")
        
        target.use375af = ini.get("ActiveFire", "use375af")              # Flag to use M-band 750 m active fire data, AVAFO (y or n)  
        target.use750af = ini.get("ActiveFire", "use750af")              # Flag to use I-band 375 m active fire data, VF375 (y or n)
        
        target.M07UB = float(ini.get("Thresholds", "M07UB"))     #Band 07 (0.86 um)upper bound
        target.M08LB = float(ini.get("Thresholds", "M08LB"))     #Band 08 (1.24 um)lower bound
        target.M08UB = float(ini.get("Thresholds", "M08UB"))     #Band 08 (1.24 um)upper bound
        target.M10LB = float(ini.get("Thresholds", "M10LB"))     #Band 10 (1.61 um)lower bound
        target.M10UB = float(ini.get("Thresholds", "M10UB"))     #Band 10 (1.61 um)upper bound
        target.M11LB = float(ini.get("Thresholds", "M11LB"))     #Band 11 (2.25 um)lower bound
        target.RthSub= float(ini.get("Thresholds", "RthSub"))   #RthSub is the factor subtracted from the 1.240 band when comparing to the Rth
        target.Rth   = float(ini.get("Thresholds", "Rth"))         #Rth
        target.RthLB = float(ini.get("Thresholds", "RthLB"))     #RthLB is the factor that the Rth check must be greater than or equal to
        target.MaxSolZen = float(ini.get("Thresholds", "MaxSolZen")) #Maximum solar zenith angle, used to filter out night pixels from burned area thresholding 


        target.TemporalProximity = int(ini.get("ConfirmBurnParameters", "TemporalProximity"))
        target.SpatialProximity  = int(ini.get("ConfirmBurnParameters", "SpatialProximity")) 

        target.TextOut = ini.get("OutputFlags", "TextFile").lower()
        target.ShapeOut = ini.get("OutputFlags", "ShapeFile").lower()
        target.DatabaseOut = ini.get("OutputFlags", "PostGIS").lower()
        target.ShapePath = ini.get("OutputFlags", "OutShapeDir")
        target.PostBin = ini.get("OutputFlags", "PostgresqlBin")
        
        target.ImageDates = ini.get("ImageDates", "ImageDates").split(',')
        
        target.DBname = ini.get("DataBaseInfo", "DataBaseName")
        target.DBuser = ini.get("DataBaseInfo", "UserName")
        target.DBschema = ini.get("DataBaseInfo", "Schema")
        target.pwd = ini.get("DataBaseInfo", "password")
        if ini.has_option("DataBaseInfo", "Host") : 
            target.DBhost = ini.get("DataBaseInfo", "Host")
        else : 
            target.DBhost = None

        if ini.has_section('GeogWindow') : 
            target.north = ini.getfloat('GeogWindow','North')
            target.south = ini.getfloat('GeogWindow','South')
            target.east  = ini.getfloat('GeogWindow','East')
            target.west  = ini.getfloat('GeogWindow','West')
        
        target.parse_schema()
        target.sort_dates()
        
        return target
        
    def get_sql_interval(self) :  
        """returns a string to represent temporalproximity as sql interval"""
        return "{0} days".format(self.TemporalProximity)
        
    def perturb_dir(self, orig_dir) :
        """sets a new directory name based on the run_id of this object and an
        example directory name for a different object. This method always 
        ensures that the output directories for all runs live at the same 
        place in the filesystem (in the same containing directory.)"""
        base = os.path.dirname(orig_dir)
        return os.path.join(base, 'Run_{:04d}'.format(self.run_id))
        
    def perturb_schema(self) :
        """modifies the schema name based on the run id"""
        self.DBschema = 'Run_{:04d}'.format(self.run_id)

    def parse_schema(self) : 
        """sets this object's run_id from the schema name"""
        m = re.match('Run_([0-9]+)', self.DBschema) 
        if m is not None : 
            self.run_id = int(m.group(1))
        
    @classmethod
    def create_run_id(cls, obj) : 
        """run id is a unique identifier for this set of parameters.
        This might be calculatable from the instance values, but may also be a 
        global counter. Therefore, ensure you create a run id only once per
        object creation. The default is just the hash of the object"""
        return hash(obj)
        
    def get_ini_obj(self) :
        """creates and returns an equivalent ConfigParser instance"""
        fltfmt = '{:4.2f}'
        ini = ConfigParser() 
        
        ini.add_section("InDirectory")
        ini.set("InDirectory", "BaseDirectory", self.BaseDir)
        
        ini.add_section("ActiveFire")
        ini.set("ActiveFire", "use375af",self.use375af.lower())              # Flag to use M-band 750 m active fire data, AVAFO (y or n)  
        ini.set("ActiveFire", "use750af",self.use750af.lower())              # Flag to use I-band 375 m active fire data, VF375 (y or n)

        ini.add_section("Thresholds")
        ini.set("Thresholds", "M07UB", fltfmt.format(self.M07UB))     #Band 07 (0.86 um)upper bound
        ini.set("Thresholds", "M08LB", fltfmt.format(self.M08LB))     #Band 08 (1.24 um)lower bound
        ini.set("Thresholds", "M08UB", fltfmt.format(self.M08UB))     #Band 08 (1.24 um)upper bound
        ini.set("Thresholds", "M10LB", fltfmt.format(self.M10LB))     #Band 10 (1.61 um)lower bound
        ini.set("Thresholds", "M10UB", fltfmt.format(self.M10UB))     #Band 10 (1.61 um)upper bound
        ini.set("Thresholds", "M11LB", fltfmt.format(self.M11LB))     #Band 11 (2.25 um)lower bound
        ini.set("Thresholds", "RthSub", fltfmt.format(self.RthSub))   #RthSub is the factor subtracted from the 1.240 band when comparing to the Rth
        ini.set("Thresholds", "Rth", fltfmt.format(self.Rth))         #Rth
        ini.set("Thresholds", "RthLB", fltfmt.format(self.RthLB))     #RthLB is the factor that the Rth check must be greater than or equal to
        ini.set("Thresholds", "MaxSolZen",fltfmt.format(self.MaxSolZen)) #Maximum solar zenith angle, used to filter out night pixels from burned area thresholding 

        ini.add_section("ConfirmBurnParameters")
        ini.set("ConfirmBurnParameters", "TemporalProximity", 
                   '{:d}'.format(self.TemporalProximity))
        ini.set("ConfirmBurnParameters", "SpatialProximity", 
                   '{:d}'.format(self.SpatialProximity))

        ini.add_section("OutputFlags")
        ini.set("OutputFlags", "TextFile", self.TextOut.lower())
        ini.set("OutputFlags", "ShapeFile", self.ShapeOut.lower())
        ini.set("OutputFlags", "PostGIS", self.DatabaseOut.lower())
        ini.set("OutputFlags", "OutShapeDir", self.ShapePath)
        ini.set("OutputFlags", "PostgresqlBin",self.PostBin)
        
        ini.add_section("ImageDates")
        ini.set("ImageDates", "ImageDates", ','.join(self.ImageDates))
        
        ini.add_section("DataBaseInfo")
        ini.set("DataBaseInfo", "DataBaseName", self.DBname)
        ini.set("DataBaseInfo", "UserName", self.DBuser)
        ini.set("DataBaseInfo", "Schema", self.DBschema)
        ini.set("DataBaseInfo", "password", self.pwd)
        if self.DBhost is not None : 
            ini.set("DataBaseInfo", "Host", self.DBhost)

        if self.has_window() : 
            ini.add_section("GeogWindow")
            fmtfmt = '{}'
            ini.set("GeogWindow", "North", fltfmt.format(self.north)) 
            ini.set("GeogWindow", "South", fltfmt.format(self.south)) 
            ini.set("GeogWindow", "East", fltfmt.format(self.east)) 
            ini.set("GeogWindow", "West", fltfmt.format(self.west)) 
        
        return ini
        
    def save(self, filename) : 
        """saves current configuration in ini format"""
        ini = self.get_ini_obj()
        f = file(filename, 'w')
        ini.write(f)
        f.close() 
        
    def sort_dates(self) : 
        self.SortedImageDates = sorted(self.ImageDates)

    def has_window(self) : 
        """checks for presence of geographic window on this object"""
        return hasattr(self,"north")
        
    def get_vector(self) : 
        """returns the vector representation of the numeric parameters
        
        This essentially includes the [Thresholds] and [ConfirmBurnParameters]
        sections."""
        params_dict = {} 
        for p in float_vector_params :
            params_dict[p] = float(getattr(self, p))
        for p in int_vector_params : 
            params_dict[p] = int(getattr(self, p))
        return ConfigVector(**params_dict) 
        
class SequentialVIIRSConfig (VIIRSConfig) : 
    _run = 0 
    
    @classmethod
    def create_run_id(cls,obj) : 
        """returns and increments run counter."""
        val = cls._run
        cls._run += 1
        return val       
