"""
Copyright (C) 2009-2013 Jussi Leinonen

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import numpy as np
from scipy.integrate import dblquad


rad_to_deg = 180.0/np.pi
deg_to_rad = np.pi/180.0


def sca_intensity(scatterer, h_pol=True):
    """Scattering intensity (phase function) for the current setup.    

    Args:
        scatterer: a Scatterer instance.
        h_pol: If true (default), use horizontal polarization.
        If false, use vertical polarization.

    Returns:
        The differential scattering cross section.
    """
    Z = scatterer.get_Z()
    return (Z[0,0] - Z[0,1]) if h_pol else (Z[0,0] + Z[0,1])
            
            
def ldr(scatterer, h_pol=True):
    """
    Linear depolarizarion ratio (LDR) for the current setup.

    Args:
        scatterer: a Scatterer instance.
        h_pol: If true (default), return LDR_h.
        If false, return LDR_v.

    Returns:
       The LDR.
    """
    Z = scatterer.get_Z()
    if h_pol:
        return (Z[0,0] - Z[0,1] + Z[1,0] - Z[1,1]) / \
               (Z[0,0] - Z[0,1] - Z[1,0] + Z[1,1])
    else:
        return (Z[0,0] + Z[0,1] - Z[1,0] - Z[1,1]) / \
               (Z[0,0] + Z[0,1] + Z[1,0] + Z[1,1])


def sca_xsect(scatterer, h_pol=True):
    old_geom = scatterer.get_geometry()    

    def d_xsect(thet, phi):
        (scatterer.phi, scatterer.thet) = (phi*rad_to_deg, thet*rad_to_deg)        
        Z = scatterer.get_Z()        
        I = sca_intensity(scatterer, h_pol)
        return I * np.sin(thet)

    xsect = dblquad(d_xsect, 0.0, 2*np.pi, lambda x: 0.0, lambda x: np.pi)[0]

    scatterer.set_geometry(old_geom)

    return xsect

       
def ext_xsect(scatterer, h_pol=True):
    """Extinction cross section for the current setup, with polarization.    

    Args:
        scatterer: a Scatterer instance.
        h_pol: If true (default), use horizontal polarization.
        If false, use vertical polarization.

    Returns:
        The extinction cross section.
        
    NOTE: The scatterer object should be set to forward scattering geometry 
    before calling this function.
    """
    if (scatterer.thet0 != scatterer.thet) or \
        (scatterer.phi0 != scatterer.phi):

        raise ValueError("A forward scattering geometry is needed to " + \
            "compute the extinction cross section.")

    S = scatterer.get_S()
    if h_pol:
        return 2 * scatterer.wavelength * S[1,1].imag
    else:
        return 2 * scatterer.wavelength * S[0,0].imag


def ssa(scatterer, h_pol=True):
    """Single-scattering albedo for the current setup, with polarization.    

    Args:
        scatterer: a Scatterer instance.
        h_pol: If true (default), use horizontal polarization.
        If false, use vertical polarization.

    Returns:
        The single-scattering albedo.
    """

    return sca_xsect(scatterer, h_pol=h_pol)/ext_xsect(scatterer, h_pol=h_pol)


def asym(scatterer, h_pol=True):
    """Asymmetry parameter for the current setup, with polarization.    

    Args:
        scatterer: a Scatterer instance.
        h_pol: If true (default), use horizontal polarization.
        If false, use vertical polarization.

    Returns:
        The asymmetry parameter.
    """

    old_geom = scatterer.get_geometry()

    cos_t0 = np.cos(scatterer.thet0 * deg_to_rad)
    sin_t0 = np.sin(scatterer.thet0 * deg_to_rad)
    p0 = scatterer.phi0 * deg_to_rad
    def integrand(thet, phi):
        (scatterer.phi, scatterer.thet) = (phi*rad_to_deg, thet*rad_to_deg)
        cos_T_sin_t = 0.5 * (np.sin(2*thet)*cos_t0 + \
            (1-np.cos(2*thet))*sin_t0*np.cos(p0-phi))
        I = sca_intensity(scatterer, h_pol)
        return I * cos_T_sin_t

    cos_int = dblquad(integrand, 0.0, 2*np.pi, lambda x: 0.0, 
        lambda x: np.pi)[0]

    scatterer.set_geometry(old_geom)

    return cos_int/sca_xsect(scatterer, h_pol)



      
            
