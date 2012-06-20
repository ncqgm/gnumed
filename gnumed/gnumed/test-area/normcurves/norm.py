#!/usr/bin/python2
###############################################################
# norm.py
# Author:       Christof Meigen (christof@nicht-ich.de)
# Copyright:    author
# License:      GPL v2 or later
# Last Changed: 13 sep 2002
###############################################################
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/test-area/normcurves/norm.py,v $
__version__ = "$Revision: 1.3 $"

'''
Classes and routines for medical normcurves.

Short intro: For anything that can be measured, there are ranges of
normality and it is often instructive to check wether measured value
is in that range or how repeated measurements at different ages behave
in comparison to the normal development.

This module provides classes that handle norms and do basically allow
to check values and get the information needed for graphical presentation.

Norm may differ for various ethnic groups, sexes etc. The selection
of the right norm can only partly be automatized and does not bother
us here. We just provide a norm that may depend on one additional
numerical parameter, which will be in most cases age, but can of course
be anything, also category codes.

A result of a check contains always a Landmark-Code, which can be used
to highlight entrys or to check plausibility during the input of values.

The central class is, which comes as no surprise, Norm. Have a look at
that. There are some examples included to show that a variety of
norm-types can be incorporated.

TO-DO:
- A SQL-representation of the norms.
- A Norm-manager as a higher level interface to check whole patients
  with all their measurements, and selects the right norm for
  every value, based on measurement types, gender of the patient
  and probably explicit selection of a norm (depends on development
  on the Patient-Object (gmCachedPerson) and application-wide
  standards for measurement-types)
- Feedback: what other typed of norms (depending on more than
  one parameter, measurements being functions) are needed?
- Development of standard-graphics like our beloved centile
  curves with height/weight in one sheet. What kind of graphics
  would be used to allow both high-quality printing and
  viewing within the application?
'''

import math


# Landmark codes are used to specify what the value of
# a measurement is like. There are exactly 10 possibilities
# which are and always will be
LandmarkCodes={
   -4 : 'unplausibly low' , 
   -3 : 'extremely low' ,
   -2 : 'critically low' ,
   -1 : 'remarkable low' ,
    0 : 'normal' ,
    1 : 'remakable high' ,
    2 : 'critically high' ,
    3 : 'extremely high' ,
    4 : 'unplausibly high' ,
 None : 'don''t know' }

# Landmark codes can be specified directly by a Norm, but usually
# a norm gives centiles or Sds. It is a matter of taste to assign
# landmarks to certain centiles or Sds-Values. This is a reasonable
# proposal, but you can change the mapping for any Norm.

GenericLandmarkSds=(-5,
                    -2.5758, # 0.05th centile
                    -1.881,  # 3rd centile
                    -1.28155,# 10th centile
                    0,       # 50th centile
                    1.28155, # 90th centile
                    1.881,   # 97th centile
                    2.5758,  # 99.5th centile
                    5)


class Curve:
    '''A Curve is a simple funktion IR => IR, still abstract'''
    def getValue(self, x):
        pass

    def getRange(self):
        pass


class ConstantCurve(Curve):
    '''A ConstantCurve is a Curve the value of which is
    independent of the parameter x'''
    def __init__(self, value):
        self.value=value
        
    def getValue(self,x=None):
        return self.value
    


class PiecewiseCurve(Curve):
    '''defined by pieces which are assigned to certain X-Values
    or intervalls'''
    def __init__(self, points):
        self.points=points[:]

    def getPos(self,x):
        '''get the (lower) position in the array of points
        for interpolation or whatever'''
        pos1=0
        if (x>self.points[-1][0]):
            return len(self.points)-1
        pos2=len(self.points)-1
        if (x<self.points[0][0]):
            raise ValueError, "X-Value out of range in PiecewiseCurve"
        while(pos2-pos1>1):
            midpos=(pos1+pos2)/2
            midval=self.points[midpos][0]
            if midval>x:
                pos2=midpos
            else:
                pos1=midpos
        return pos1

    def addPoint(self, p):
        pos=len(self.points)
        while ((self.points[pos][0]>p[0]) and
               (pos>0)):
            pos-=1
        self.points=self.points[:pos]+[p]+self.points[pos:]


class PolygonCurve(PiecewiseCurve):
    '''A Curve defined by (x,y)-Pairs, between linear interpolation
    is used.'''
    
    def getValue(self, x):
        pos1=self.getPos(x)
        if (pos1==len(self.points)-1):
            raise ValueError, "X-Value too large in PolygonCurve"
        return self.points[pos1][1]+(x-self.points[pos1][0])/  \
               (self.points[pos1+1][0]-self.points[pos1][0])*  \
               (self.points[pos1+1][1]-self.points[pos1][1])


    def getRange(self):
        return [self.points[0][0], self.points[-1][0]]


class SplineCurve(PiecewiseCurve):
    '''A Curve defined by a list of lists:
    (xmin, xmax, coefficients ....)
    where coefficients define a polynom of x, with
    the coefficient for the highest power first'''

    def getValue(self, x):
        pos=self.getPos(x)
        if (x>self.points[pos][1]):
            raise ValueError, "X-Value too large or in a gap; in SplineCurve"
        result=self.points[pos][2]
        for i in range(3, len(self.points[pos])):
            result = result * x + self.points[pos][i]
        return result

    def getRange(self):
        return [self.points[0][0], self.points[-1][1]]
        
class Norm:
    '''A norm is the most abstract thing that can check
    values. A check returns a dictionary that has
    always an Element "landmark" as explained above.
    It may have elements "centile" and "sds" containing
    the individual centile and sds of the value in question
    and it may also have elements "above_centile" and
    "below_centile" stating it is above or below certain
    centiles specified by the normcurve.

    valueOfLandmark and valueOfCentile can be used to
    draw those nice lines in charts. Before you use them,
    check first what Landmarks/Centiles are actually
    avaliable in the specific norm
    '''

    def __init__(self):
        pass

    def checkValue(self,val, x=None):
        pass

    def getRange(self):
        '''return the range of the x-Value as Pair'''
        pass

    def availableLandmarks(self):
        '''This returns a list of numbers == Landmark-Codes,
        that are used in this norm'''
        return None

    def availableCentiles(self):
        '''returns a list of available centiles, or an empty list
        for "any centile" '''
        return None

    def valueOfCentile(self, centile, x=None):
        pass

    def valueOfLandmark(self, lm, x=None):
        pass

class SdsNorm(Norm):
    ''' An abstract class for Norms that assign a SDS (aka standard
    deviation score) to an value. It is used to provide a conversion to
    centiles'''

    def __init__(self,LandmarkSds=GenericLandmarkSds):
        self.LandmarkSds=LandmarkSds
       
 
    def sds2Centile(self, sds):
        '''This function uses Chebycev-polynoms of degree 5 to approximate
        the centile (the quantile function) of a sds value. While certainly
        not being very accurate, you can rely on the first 3 digits'''
        
        T=[0,0,0,0,0,0]
        Chebycevs = [
            [0.4973666604,  0.3593245663, -0.0030377998,
             -0.0124184017, -0.0004268668, 0.0005668759] ,
            # 1-2
            [0.728022111,  0.345609565, -0.123632995,
             0.035881301, -0.010643323, 0.002190653] , 
            # 2-3
            [0.853363319,  0.242028055, -0.144689610,
             0.065571773, -0.021307699, 0.003932716] ,
            # 3-4
            [0.884041528,  0.204193385, -0.138315372,
             0.070043127, -0.024329369, 0.004642137]];

        centile=0
        if sds>0:
            sign=0
        else:
            sign=1
        sds=abs(sds)
        if sds>4:
            centile=1
        else:
            arraypos=int(sds)
            sds=sds-arraypos
            T[0]=1    # recursive evaluation of the chebycev-polynoms
            T[1]=sds
            for i  in range(2,6):
                T[i]=2*sds*T[i-1]-T[i-2]
            for i in range(0,6):
                centile += T[i]*Chebycevs[arraypos][i]
        if sign:
            centile=1-centile
        return 100*centile



    def centile2Sds(self,centile):
        '''This function converts a given centile (btween 0 and 100) to an
        standard deviation score. sds higher than 4 or lower than -4 are
        cut to these values. This function is not highly accurate, but
        you can on rely on the first three digits (for the centile).

        More detailed: The chebychevs are for the intervalls between the
        centile for sds 0-1, 1-2 etc. centile values in these intervalls
        are normalized to the range -1 -- 1. The Polynoms are noted with
        absolute coefficient first'''
        T=[0,0,0,0,0,0]
        Chebycevs = [
            [0.4695971, 0.4923128, 0.0289830,
             0.0073152, 0.00118679, 0.0002631095],
            [1.410083615, 0.473275921, 0.079708293,
             0.022242266, 0.006375791, 0.001941458],
            [2.353389606, 0.437082375, 0.111203044,
             0.040549727, 0.014375307, 0.005346785],
            [3.30055673, 0.38822658, 0.12026134,
             0.05073124, 0.01988737, 0.00810505]]
        pnorms = [0.5, 0.8413447, 0.9772499, 0.9986501 , 0.9999683]
        sign=1
        if centile<50:
            centile=100-centile
            sign=-1
        centile /=100.0
        if centile>=pnorms[-1]:
            return sign*4
        pos=0
        while pnorms[pos+1]<centile:
            pos+=1
        x=2*(centile-pnorms[pos])/(pnorms[pos+1]-pnorms[pos])-1
        sds=0
        T[0]=1    # recursive evaluation of the chebycev-polynoms
        T[1]=x
        for i  in range(2,6):
            T[i]=2*x*T[i-1]-T[i-2]
        for i in range(0,6):
            sds += T[i]*Chebycevs[pos][i]
        return sign*sds
        
    def centileOfValue(self, val, x=None):
        return self.sds2Centile(self.sdsOfValue(val, x))

    def valueOfCentile(self, centile, x=None):
        return self.valueOfSds(self.centile2Sds(centile), x)
        
    def sdsOfValue(self, val, x=None):
        pass
    
    def valueOfSds(self, sds, x=None):
        pass

    def checkValue(self,val, x=None):
        check={'below_centile': None, 'above_centile': None}
        check['sds']=self.sdsOfValue(val,x)
        check['centile']=self.sds2Centile(check['sds'])

        if check['sds']>=self.LandmarkSds[-1]:
            check['landmark']=4
        else:
            pos=0
            while ((pos<len(self.LandmarkSds)) and
                   (check['sds']>self.LandmarkSds[pos])):
                pos +=1
            if (pos>4):
                pos-=1
            check['landmark']=pos-(len(self.LandmarkSds)/2)
        return check
        
    def availableCentiles(self):
        return []

    def availableLandmarks(self):
        return range(-4,5)

    def valueOfLandmark(self, lm,x=None):
        return valueOfSds(self.LandmarkSds[lm+4],x)
        
        

    

class NormalDistribution(SdsNorm):
    '''A class for normal (gaussian) distributed values '''
    def __init__(self, mean, sigma, LandmarkSds=GenericLandmarkSds):
        SdsNorm.__init__(self, LandmarkSds)
        self.mean=mean
        self.sigma=sigma

    def sdsOfValue(self, val, x=None):
        return (val-self.mean.getValue(x))/self.sigma.getValue(x)
        
    def valueOfSds(self, sds, x=None):
        return self.mean.getValue(x)+sds*self.sigma.getValue(x)

    def getRange(self):
        mrange=self.mean.getRange();
        srange=self.sigma.getRange();
        return [max(mrange[0],srange[0]),
                min(mrange[1], srange[1])]


class LogNormalDistribution(NormalDistribution):
    '''A log-normal distribution describes a value whose log
    is normally distributed. While being in principle a
    skew normal distribution with bc_power=0, this class
    allows for different bases of the log.'''

    def __init__(self, mean, sigma, # two curves
                 LandmarkSds=GenericLandmarkSds,
                 basis=10):
        NormalDistribution.__init__(self,mean, sigma, LandmarkSds)
        self.basis=basis

    def sdsOfValue(self, val, x=None):
        val=math.log(val)/math.log(self.basis)
        return NormalDistribution.sdsOfValue(self, val, x)

    def valueOfSds(self, sds, x=None):
        val=NormalDistribution.valueOfSds(self, sds, x)
        return basis**val



class SkewNormalDistribution(SdsNorm):
    '''A class for values which are normally distributed after
    a Box-Cox-Transformation, which is basically raising the
    value to bc_power compensating for skewness'''

    def __init__(self, mean,
                 sigma,
                 bc_power, # three curves
                 LandmarkSds=GenericLandmarkSds):
        SdsNorm.__init__(self, LandmarkSds)
        self.mean=mean
        self.sigma=sigma
        self.bc_power=bc_power

    def sdsOfValue(self, val, x=None):
        m=self.mean.getValue(x)
        s=self.sigma.getValue(x)
        l=self.bc_power.getValue(x)

        if (abs(l)<1e-4):
            return math.log(val/m)/s
        else:
            return ((val/m)**l - 1)/(l*s)

    
    def valueOfSds(self, sds, x=None):
        m=self.mean.getValue(x)
        s=self.sigma.getValue(x)
        l=self.bc_power.getValue(x)
        if (abs(l)< 1e-4):
            return m*exp(s*sds)
        else:
            return m* (1+l*s*sds)**(1/l)


    def getRange(self):
        nrange=NormalDistribution.getRange(self)
        lrange=self.bc_power.getRange(self)
        return [max(nrange[0],lrange[0]),
                min(nrange[1],lrange[1])]



class SelectedCurves(Norm):
    '''A class for Norms were selected curves, for example
    for some centiles, are given.'''

    def __init__(self, ListOfCurves):

        '''The ListOfCurves is a List of dictionaries, each containing
        a "curve", a "landmark", possibly a "centile".

        It makes perfect sense give just one curve. For a positive
        landmark, all values below that curve are normal, for
        a negative landmark, all values above that curve are normal.
        
        It is not allowed to mix centile / non-centile curves!
        The values of the Curves have to be in ascending order and
        all curves have to have the same range'''
        
        Norm.__init__(self)
        self.listofcurves=ListOfCurves
        try:
            temp=ListOfCurves[0]['centile'] 
            self.iscentilenorm=1
        except:
            self.iscentilenorm=0

    def checkValue(self,val, x=None):
        check={'sds': None,
               'centile':None,
               'above_centile': None,
               'below_centile':None}
        if val<=self.listofcurves[0]['curve'].getValue(x):
            if self.iscentilenorm:
                check['below_centile']=self.listofcurves[0]['centile']
            if self.listofcurves[0]['landmark']<0:
                check['landmark']=self.listofcurves[0]['landmark']
            else:
                check['landmark']=0
            return check
        if val>=self.listofcurves[-1]['curve'].getValue(x):
            if self.iscentilenorm:
                check['above_centile']=self.listofcurves[-1]['centile']
            if self.listofcurves[0]['landmark']>0:    
                check['landmark']=self.listofcurves[-1]['landmark']
            else:
                check['landmark']=0
            return check
        pos1=0
        pos2=len(self.listofcurves)
        while(pos2-pos1>1):
            midpos=(pos1+pos2)/2
            midval=self.listofcurves[midpos]['curve'].getValue(x)
            if midval>val:
                pos2=midpos
            else:
                pos1=midpos
        if self.iscentilenorm:
            check['above_centile']=self.listofcurves[pos1]['centile']
            check['below_centile']=self.listofcurves[pos2]['centile']
        if self.listofcurves[pos1]['landmark']<0:
            if self.listofcurves[pos2]['landmark']>0:
                check['landmark']=0
            else:
                check['landmark']=self.listofcurves[pos2]['landmark']
        else:
            check['landmark']=self.listofcurves[pos1]['landmark']
        return check



    def availableStuff(self, what):
        '''This and the next function are like "private", they
        generalize the availableCentiles, avaliableLandmarks etc.'''
        c=[]
        for curve in ListOfCurves:
            try:
                c += curve[what]
            except:
                pass
        if len(c)==0:
            return None
        else:
            return c

    def valueOfStuff(self, what, val, x=None):
        pos=0
        while ((pos<len(self.listofcurves)) &
               (self.listofcurves[pos][what] != val)):
            pos +=1
        if (pos == len(self.listofcurves)):
            raise ValueError, "No such centile or landmark"
        return self.listofcurves[pos]['curve'].getValue(x)


    
    def availableCentiles(self):
        return self.availableStuff('centile')
        
    def availableLandmarks(self):
        return self.availableStuff('landmark')

    def valueOfCentile(self, centile, x=None):
        return self.valueOfStuff('centile', centile, x)

    def valueOfLandmark(self, lm, x=None):
        return self.valueOfStuff('landmark', lm, x)

    def getRange(self):
        '''FIXME: All curves have to have the same range'''
        return self.listofcurves[0]['curve'].getRange()

######################################################################
# JUST FOR TESTING PURPOSES
# These curves are provided just as examples for different
# styles of normcurves. 
# The female height and weight centiles are taken from Prader et al,
# Helvetica Paediatrica Acta, 1989, and are based on a longitudinal survey.
# The female BMI is an unpublished curve based on children from Leipzig,
# the weight values for the Turner-girls are from Acta
# Paeditrica 86:937-42, 1997
# 
######################################################################


if __name__=="__main__":

    female_height_mean = PolygonCurve([
        [0    ,   49.9    ],   
        [0.25 ,   59.5    ],
        [0.5  ,   66.1    ],
        [0.75 ,   70.9    ],
        [1    ,   74.5    ],
        [1.5  ,   80.8    ],
        [2    ,   86.6    ],
        [3.0  ,   95.61   ],
        [4.0  ,   102.97  ],
        [5.0  ,   109.61  ],
        [6.0  ,   115.85  ],
        [7.0  ,   122.02  ],
        [8.0  ,   127.83  ],
        [9.0  ,   133.64  ],
        [9.5  ,   135.87  ],
        [10.0 ,   138.42  ],
        [10.5 ,   141.09  ],
        [11.0 ,   144.29  ],
        [11.5 ,   146.88  ],
        [12.0 ,   150.11  ],
        [12.5 ,   153.23  ],
        [13.0 ,   155.74  ],
        [13.5 ,   158.21  ],
        [14.0 ,   160.07  ],
        [14.5 ,   161.91  ],
        [15.0 ,   162.74  ],
        [15.5 ,   163.46  ],
        [16.0 ,   163.99  ],
        [17.0 ,   164.53  ],
        [18.0 ,   164.40  ],
        [19.0 ,   164.43  ],
        [20.0 ,   164.62  ]])


    female_height_sigma = PolygonCurve([
        [0    , 1.9   ],   
        [0.25 , 2     ],
        [0.5  , 2     ],
        [0.75 , 2.2   ],
        [1    , 2.5   ],
        [1.5  , 2.4   ],
        [2    , 2.5   ],
        [3.0  , 3.23  ],
        [4.0  , 3.71  ],
        [5.0  , 4.00  ],
        [6.0  , 4.26  ],
        [7.0  , 4.58  ],
        [8.0  , 4.69  ],
        [9.0  , 5.00  ],
        [9.5  , 5.47  ],
        [10.0 , 5.64  ],
        [10.5 , 6.01  ],
        [11.0 , 5.95  ],
        [11.5 , 6.58  ],
        [12.0 , 6.81  ],
        [12.5 , 6.73  ],
        [13.0 , 6.60  ],
        [13.5 , 6.25  ],
        [14.0 , 5.84  ],
        [14.5 , 5.77  ],
        [15.0 , 5.75  ],
        [15.5 , 5.64  ],
        [16.0 , 5.74  ],
        [17.0 , 5.86  ],
        [18.0 , 5.84  ],
        [19.0 , 5.89  ],
        [20.0 , 5.92  ]])
    
    female_weight_3rdcentile = PolygonCurve([
        [0    , 2.4      ],   
        [0.25 , 4.2      ],
        [0.5  , 5.8      ],
        [0.75 , 7        ],
        [1    , 7.8      ],
        [1.5  , 9        ],
        [2    , 9.8      ],
        [3.0  , 11.3     ],
        [4.0  , 13       ],
        [5.0  , 14.5     ],
        [6.0  , 15.9     ],
        [7.0  , 17.7     ],
        [8.0  , 19.5     ],
        [9.0  , 21.3     ],
        [9.5  , 22.3     ],
        [10.0 , 23.5     ],
        [10.5 , 24.7     ],
        [11.0 , 26       ],
        [11.5 , 27.4     ],
        [12.0 , 29       ],
        [12.5 , 30.6     ],
        [13.0 , 32.4     ],
        [13.5 , 34.2     ],
        [14.0 , 35.9     ],
        [14.5 , 37.4     ],
        [15.0 , 38.8     ],
        [15.5 , 40       ],
        [16.0 , 41       ],
        [17.0 , 42.7     ],
        [18.0 , 43.7     ],
        [19.0 , 44       ],
        [20.0 , 44       ]])
    
    female_weight_10thcentile = PolygonCurve([
        [0    , 2.7      ],   
        [0.25 , 4.6      ],
        [0.5  , 6.2      ],
        [0.75 , 7.4      ],
        [1    , 8.2      ],
        [1.5  , 9.6      ],
        [2    , 10.6     ],
        [3.0  , 12.4     ],
        [4.0  , 14       ],
        [5.0  , 15.7     ],
        [6.0  , 17.3     ],
        [7.0  , 19.2     ],
        [8.0  , 21.1     ],
        [9.0  , 23.1     ],
        [9.5  , 24.2     ],
        [10.0 , 25.5     ],
        [10.5 , 26.7     ],
        [11.0 , 28.1     ],
        [11.5 , 29.7     ],
        [12.0 , 31.5     ],
        [12.5 , 33.4     ],
        [13.0 , 35.6     ],
        [13.5 , 37.8     ],
        [14.0 , 40       ],
        [14.5 , 42       ],
        [15.0 , 43.5     ],
        [15.5 , 44.7     ],
        [16.0 , 45.7     ],
        [17.0 , 46.7     ],
        [18.0 , 46.8     ],
        [19.0 , 46.5     ],
        [20.0 , 46.1     ]])

    female_weight_50thcentile = PolygonCurve([
        [0    , 3.3      ],   
        [0.25 , 5.2      ],
        [0.5  , 7        ],
        [0.75 , 8.4      ],
        [1    , 9.5      ],
        [1.5  , 10.9     ],
        [2    , 12.1     ],
        [3.0  , 14.1     ],
        [4.0  , 16.2     ],
        [5.0  , 18.2     ],
        [6.0  , 20.4     ],
        [7.0  , 23       ],
        [8.0  , 25.6     ],
        [9.0  , 28.1     ],
        [9.5  , 29.4     ],
        [10.0 , 30.8     ],
        [10.5 , 32.3     ],
        [11.0 , 34.1     ],
        [11.5 , 36.4     ],
        [12.0 , 39.1     ],
        [12.5 , 41.8     ],
        [13.0 , 44.3     ],
        [13.5 , 46.9     ],
        [14.0 , 49.2     ],
        [14.5 , 50.8     ],
        [15.0 , 51.7     ],
        [15.5 , 52.3     ],
        [16.0 , 52.9     ],
        [17.0 , 54.1     ],
        [18.0 , 54.5     ],
        [19.0 , 54.6     ],
        [20.0 , 54.6     ]])

    female_weight_90thcentile = PolygonCurve([
        [0    , 3.8      ],   
        [0.25 , 5.9      ],
        [0.5  , 7.9      ],
        [0.75 , 9.5      ],
        [1    , 10.7     ],
        [1.5  , 12.4     ],
        [2    , 13.6     ],
        [3.0  , 16.3     ],
        [4.0  , 18.5     ],
        [5.0  , 20.7     ],
        [6.0  , 23.1     ],
        [7.0  , 26       ],
        [8.0  , 29.6     ],
        [9.0  , 33.9     ],
        [9.5  , 36.3     ],
        [10.0 , 38.9     ],
        [10.5 , 41.6     ],
        [11.0 , 44.5     ],
        [11.5 , 47.4     ],
        [12.0 , 50.3     ],
        [12.5 , 53       ],
        [13.0 , 55.6     ],
        [13.5 , 58       ],
        [14.0 , 60.1     ],
        [14.5 , 61.9     ],
        [15.0 , 63.3     ],
        [15.5 , 64.4     ],
        [16.0 , 65.2     ],
        [17.0 , 65.9     ],
        [18.0 , 65.9     ],
        [19.0 , 65.7     ],
        [20.0 , 65.5     ]])

    female_weight_97thcentile = PolygonCurve([
        [0    , 4    ],   
        [0.25 , 6.3  ],
        [0.5  , 8.4  ],
        [0.75 , 10.1 ],
        [1    , 11.3 ],
        [1.5  , 13   ],
        [2    , 14.3 ],
        [3.0  , 17.3 ],
        [4.0  , 19.5 ],
        [5.0  , 22   ],
        [6.0  , 25.2 ],
        [7.0  , 29   ],
        [8.0  , 32.4 ],
        [9.0  , 37.1 ],
        [9.5  , 39.5 ],
        [10.0 , 42.2 ],
        [10.5 , 45.4 ],
        [11.0 , 48.8 ],
        [11.5 , 52.4 ],
        [12.0 , 55.7 ],
        [12.5 , 58.6 ],
        [13.0 , 61.2 ],
        [13.5 , 63.4 ],
        [14.0 , 65.5 ],
        [14.5 , 67.6 ],
        [15.0 , 69.8 ],
        [15.5 , 71.9 ],
        [16.0 , 73.8 ],
        [17.0 , 76.3 ],
        [18.0 , 77   ],
        [19.0 , 75.9 ],
        [20.0 , 73.4 ]])


    female_bmi_bc = PolygonCurve( [
       [  0.00 ,  -0.141   ] ,
       [  0.10 ,  0.245    ] ,
       [  0.24 ,  -0.236   ] ,
       [  0.40 ,  -0.273   ] ,
       [  0.56 ,  -0.277   ] ,
       [  0.72 ,  -1.271   ] ,
       [  1.00 ,  -0.479   ] ,
       [  1.50 ,  -0.640   ] ,
       [  2.00 ,  -0.644   ] ,
       [  2.50 ,  -0.583   ] ,
       [  3.00 ,  -0.726   ] ,
       [  3.50 ,  -0.731   ] ,
       [  4.00 ,  -0.778   ] ,
       [  4.50 ,  -1.009   ] ,
       [  5.00 ,  -1.066   ] ,
       [  5.50 ,  -1.277   ] ,
       [  6.00 ,  -1.748   ] ,
       [  6.50 ,  -1.363   ] ,
       [  7.00 ,  -1.487   ] ,
       [  7.50 ,  -1.069   ] ,
       [  8.00 ,  -1.195   ] ,
       [  8.50 ,  -1.487   ] ,
       [  9.00 ,  -1.254   ] ,
       [  9.50 ,  -1.258   ] ,
       [ 10.00 ,  -1.155   ] ,
       [ 10.50 ,  -1.044   ] ,
       [ 11.00 ,  -1.153   ] ,
       [ 11.50 ,  -1.013   ] ,
       [ 12.00 ,  -1.012   ] ,
       [ 12.50 ,  -0.675   ] ,
       [ 13.00 ,  -1.078   ] ,
       [ 13.50 ,  -1.209   ] ,
       [ 14.00 ,  -1.318   ] ,
       [ 14.50 ,  -1.125   ] ,
       [ 15.00 ,  -1.199   ] ,
       [ 15.50 ,  -1.040   ] ,
       [ 16.00 ,  -1.544   ] ,
       [ 17.00 ,  -1.359   ] ,
       [ 18.00 ,  -1.249   ] ])

    female_bmi_median = PolygonCurve( [
       [  0.00 , 13.060  ] ,
       [  0.10 , 14.384  ] ,
       [  0.24 , 15.690  ] ,
       [  0.40 , 16.357  ] ,
       [  0.56 , 16.648  ] ,
       [  0.72 , 16.534  ] ,
       [  1.00 , 16.546  ] ,
       [  1.50 , 16.209  ] ,
       [  2.00 , 15.945  ] ,
       [  2.50 , 15.718  ] ,
       [  3.00 , 15.568  ] ,
       [  3.50 , 15.455  ] ,
       [  4.00 , 15.475  ] ,
       [  4.50 , 15.446  ] ,
       [  5.00 , 15.454  ] ,
       [  5.50 , 15.498  ] ,
       [  6.00 , 15.531  ] ,
       [  6.50 , 15.719  ] ,
       [  7.00 , 15.828  ] ,
       [  7.50 , 16.201  ] ,
       [  8.00 , 16.494  ] ,
       [  8.50 , 16.692  ] ,
       [  9.00 , 16.890  ] ,
       [  9.50 , 17.142  ] ,
       [ 10.00 , 17.513  ] ,
       [ 10.50 , 17.751  ] ,
       [ 11.00 , 18.186  ] ,
       [ 11.50 , 18.608  ] ,
       [ 12.00 , 18.851  ] ,
       [ 12.50 , 19.264  ] ,
       [ 13.00 , 19.656  ] ,
       [ 13.50 , 19.961  ] ,
       [ 14.00 , 20.365  ] ,
       [ 14.50 , 20.584  ] ,
       [ 15.00 , 20.803  ] ,
       [ 15.50 , 21.048  ] ,
       [ 16.00 , 21.133  ] ,
       [ 17.00 , 21.255  ] ,
       [ 18.00 , 21.092  ] ])


    female_bmi_s = PolygonCurve( [
       [  0.00 , 0.108   ] ,
       [  0.10 , 0.091   ] ,
       [  0.24 , 0.092   ] ,
       [  0.40 , 0.093   ] ,
       [  0.56 , 0.090   ] ,
       [  0.72 , 0.091   ] ,
       [  1.00 , 0.088   ] ,
       [  1.50 , 0.090   ] ,
       [  2.00 , 0.089   ] ,
       [  2.50 , 0.094   ] ,
       [  3.00 , 0.090   ] ,
       [  3.50 , 0.095   ] ,
       [  4.00 , 0.095   ] ,
       [  4.50 , 0.105   ] ,
       [  5.00 , 0.107   ] ,
       [  5.50 , 0.109   ] ,
       [  6.00 , 0.120   ] ,
       [  6.50 , 0.133   ] ,
       [  7.00 , 0.135   ] ,
       [  7.50 , 0.143   ] ,
       [  8.00 , 0.142   ] ,
       [  8.50 , 0.152   ] ,
       [  9.00 , 0.155   ] ,
       [  9.50 , 0.156   ] ,
       [ 10.00 , 0.160   ] ,
       [ 10.50 , 0.168   ] ,
       [ 11.00 , 0.174   ] ,
       [ 11.50 , 0.173   ] ,
       [ 12.00 , 0.177   ] ,
       [ 12.50 , 0.174   ] ,
       [ 13.00 , 0.176   ] ,
       [ 13.50 , 0.172   ] ,
       [ 14.00 , 0.165   ] ,
       [ 14.50 , 0.167   ] ,
       [ 15.00 , 0.158   ] ,
       [ 15.50 , 0.157   ] ,
       [ 16.00 , 0.154   ] ,
       [ 17.00 , 0.153   ] ,
       [ 18.00 , 0.160   ] ])


    turner_weight_mean = SplineCurve ( [
        [0,2 ,0.058955,-0.35571,0.74309, 0.47602],
        [2,17,-0.000056,0.00054, 0.0492, 0.93488]])
    turner_weight_sigma   = SplineCurve( [
        [0,2 ,-0.002435, 0.013913, 0.029735, 0.07696],
        [2,17,0.000008, -0.000507, 0.00902, 0.026574]])
   

    female_weight = SelectedCurves( [
        {'curve':female_weight_3rdcentile ,
         'centile':3 ,
         'landmark':-2} ,
        {'curve':female_weight_10thcentile ,
         'centile':10 ,
         'landmark':-1} ,
        {'curve':female_weight_50thcentile ,
         'centile':50 ,
         'landmark':0} ,
        {'curve':female_weight_90thcentile ,
         'centile':90 ,
         'landmark':1} ,
        {'curve':female_weight_97thcentile ,
         'centile':97 ,
         'landmark':2}])

    
    female_height=NormalDistribution(female_height_mean,
                                     female_height_sigma)
    
    female_bmi=SkewNormalDistribution(female_bmi_median,
                                      female_bmi_s,
                                      female_bmi_bc)

    turner_weight=LogNormalDistribution(turner_weight_mean,
                                        turner_weight_sigma)

    while 1:
        print "Choose (1) Female Height        (in cm) (Prader 1976) or"
        print "       (2) Female Weight        (in kg) (Prader 1976) or"
        print "       (3) Female BMI           (in kg/m^2) (Leipzig 2002)"
        print "       (4) Female Weight/Turner (in kg) (Rongen-Westlaken 1997)"
        nc=int(raw_input(''))
        x=float(raw_input('Age:'))
        y=float(raw_input('Value:'))
        try:
            if nc==1:
                check=female_height.checkValue(y,x)
            elif nc==2:
                check=female_weight.checkValue(y,x)
            elif nc==3:
                check=female_bmi.checkValue(y,x)
            else:
                check=turner_weight.checkValue(y,x)
                
            if check['sds'] != None:
                print "The Standard deviation score of that value is %s" % check['sds']
            if check['centile'] != None:
                print "The Value is on the %s-th centile" % check['centile']
            if check['above_centile'] != None:
                print "The value is above the %s-th centile" % check['above_centile']
            if check['below_centile'] != None:
                print "The value is below the %s-th centile" % check['below_centile']
            if check['landmark'] != None:
                print "This is considered to be %s" % LandmarkCodes[check['landmark']]
        except:
            print "The value could not be checked. Perhaps the age is out of range?"
             
