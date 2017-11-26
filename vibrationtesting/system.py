"""
Created on 14 May 2015
@author: Joseph C. Slater
"""
__license__ = "Joseph C. Slater"

__docformat__ = 'reStructuredText'


import math
import warnings

import numpy as np
# import control as ctrl
import scipy.signal as sig
import scipy.linalg as la


def d2c(Ad, Bd, C, D, dt):
    """Returns continuous A, B, C, D from discrete
    Converts a set of digital state space system matrices to their
    continuous counterpart.

    Parameters
    ----------
    Ad, Bd, C, D : float arrays
        Discrete state space system matrices
    dt  : float
        Time step of discrete system

    Returns
    -------
    A, B, C, D : float arrays
        State space system matrices

    Examples
    --------
    >>> import vibrationtesting as vt
    >>> Ad = np.array([[ 0.9999,0.0001,0.01,0.],
    ...                [ 0.,0.9999,0.,0.01],
    ...                [-0.014,0.012,0.9999,0.0001],
    ...                [ 0.008, -0.014,0.0001,0.9999]])
    >>> Bd = np.array([[ 0.  ],
    ...                [ 0.  ],
    ...                [ 0.  ],
    ...                [ 0.01]])
    >>> C = np.array([[-1.4, 1.2, -0.0058, 0.0014]])
    >>> D = np.array([[-0.2]])
    >>> A, B, *_ = vt.d2c(Ad, Bd, C, D, 0.01)
    >>> print(A)
    [[-0.003   0.004   1.0001 -0.0001]
     [-0.004  -0.003  -0.      1.0001]
     [-1.4001  1.2001 -0.003   0.004 ]
     [ 0.8001 -1.4001  0.006  -0.003 ]]

    Notes
    -----
    .. note:: Zero-order hold solution
    .. note:: discrepancies between :func:`c2d` and :func:`d2c` are due to \
    typing truncation errors.
    .. seealso:: :func:`c2d`.
    """

    # Old school (very old)
    # A = la.logm(Ad) / dt
    # B = la.solve((Ad - np.eye(A.shape[0])), A) @ Bd
    sa = Ad.shape[0]
    sb = Bd.shape[1]
    AAd = np.vstack((np.hstack((Ad,                  Bd)),
                     np.hstack((np.zeros((sb, sa)),  np.eye(sb)))))
    AA = la.logm(AAd)/dt
    A = AA[0:sa, 0:sa]
    B = AA[0:sa, sa:]
    return A, B, C, D


def c2d(A, B, C, D, dt):
    """Convert continuous state system to discrete time
    Converts a set of continuous state space system matrices to their
    discrete counterpart.

    Parameters
    ----------
    A, B, C, D : float arrays
        State space system matrices
    dt : float
        Time step of discrete system

    Returns
    -------
    Ad, Bd, C, D : float arrays
        Discrete state space system matrices

    Examples
    --------
    >>> import numpy as np
    >>> import vibrationtesting as vt
    >>> A1 = np.array([[ 0.,   0. ,  1.    ,  0.    ]])
    >>> A2 = np.array([[ 0.,   0. ,  0.    ,  1.    ]])
    >>> A3 = np.array([[-1.4,  1.2, -0.0058,  0.0014]])
    >>> A4 = np.array([[ 0.8, -1.4,  0.0016, -0.0038]])
    >>> A = np.array([[ 0.,   0. ,  1.    ,  0.    ],
    ...               [ 0.,   0. ,  0.    ,  1.    ],
    ...               [-1.4,  1.2, -0.0058,  0.0014],
    ...               [ 0.8, -1.4,  0.0016, -0.0038]])
    >>> B = np.array([[ 0.],
    ...               [ 0.],
    ...               [ 0.],
    ...               [ 1.]])
    >>> C = np.array([[-1.4, 1.2, -0.0058, 0.0014]])
    >>> D = np.array([[-0.2]])
    >>> Ad, Bd, *_ = vt.c2d(A, B, C, D, 0.01)
    >>> print(Ad)
    [[ 0.9999  0.0001  0.01    0.    ]
     [ 0.      0.9999  0.      0.01  ]
     [-0.014   0.012   0.9999  0.0001]
     [ 0.008  -0.014   0.0001  0.9999]]
    >>> print(Bd)
    [[ 0.  ]
     [ 0.  ]
     [ 0.  ]
     [ 0.01]]

    Notes
    -----
    .. note:: Zero-order hold solution
    .. seealso:: :func:`d2c`.
    """

    Ad, Bd, _, _, _ = sig.cont2discrete((A, B, C, D), dt)
    # Ad = la.expm(A * dt)
    # Bd = la.solve(A, (Ad - np.eye(A.shape[0]))) @ B
    return Ad, Bd, C, D


def ssfrf(A, B, C, D, omega_low, omega_high, in_index, out_index):
    """returns
    obtains the computed FRF of a state space system between selected input
    and output over frequency range of interest.

    Parameters
    ----------
    A, B, C, D : float arrays
                 state system matrices
    omega_low, omega_high: floats
                 low and high frequencies for evaluation
    in_index, out_index : ints
                input and output numbers (starting at 1)

    Returns
    -------
    omega : float array
            frequency vector
    H : float array
        frequency response function

    Examples
    --------
    >>> import numpy as np
    >>> import vibrationtesting as vt
    >>> A1 = np.array([[ 0.,   0. ,  1.    ,  0.    ]])
    >>> A2 = np.array([[ 0.,   0. ,  0.    ,  1.    ]])
    >>> A3 = np.array([[-1.4,  1.2, -0.0058,  0.0014]])
    >>> A4 = np.array([[ 0.8, -1.4,  0.0016, -0.0038]])
    >>> A = np.array([[ 0.,   0. ,  1.    ,  0.    ],
    ...               [ 0.,   0. ,  0.    ,  1.    ],
    ...               [-1.4,  1.2, -0.0058,  0.0014],
    ...               [ 0.8, -1.4,  0.0016, -0.0038]])
    >>> B = np.array([[ 0.],
    ...               [ 0.],
    ...               [ 0.],
    ...               [ 1.]])
    >>> C = np.array([[-1.4, 1.2, -0.0058, 0.0014]])
    >>> D = np.array([[-0.2]])
    >>> omega, H = vt.ssfrf(A, B, C, D, 0, 3.5, 1, 1)
    >>> vt.frfplot(omega, H)

    """
    # A, B, C, D = ctrl.ssdata(sys)
    sa = A.shape[0]
    omega = np.linspace(omega_low, omega_high, 1000)
    H = omega * 1j
    i = 0
    for i, w in enumerate(omega):
        H[i] = (C@la.solve(w * 1j * np.eye(sa) - A, B) + D)[out_index-1,
                                                            in_index-1]
    return omega.reshape(1, -1), H.reshape(1, -1)


def so2ss(M, C, K, Bt, Cd, Cv, Ca):
    """returns A, B, C, D
    Given second order linear matrix equation of the form
    :math:`M\\ddot{x} + C \\dot{x} + K x= \\tilde{B} u`
    and
    :math:`y = C_d x + + C_v \\dot{x} + C_a\\ddot{x}`
    returns the state space form equations
    :math:`\\dot{z} = A z + B u`,
    :math:`y = C z + D u`

    Parameters
    ----------
    M, C, K, Bt, Cd, Cv, Cd: float arrays
        Mass , damping, stiffness, input, displacement sensor, velocimeter,
        and accelerometer matrices

    Returns
    -------
    A, B, C, D: float arrays
        State matrices

    Examples
    --------
    >>> import numpy as np
    >>> import vibrationtesting as vt
    >>> M = np.array([[2, 1],
    ...               [1, 3]])
    >>> K = np.array([[2, -1],
    ...               [-1, 3]])
    >>> C = np.array([[0.01, 0.001],
    ...               [0.001, 0.01]])
    >>> Bt = np.array([[0], [1]])
    >>> Cd = Cv = np.zeros((1,2))
    >>> Ca = np.array([[1, 0]])
    >>> A, B, Css, D = vt.so2ss(M, C, K, Bt, Cd, Cv, Ca)
    >>> print('A: {}'.format(A))
    A:  [[ 0.      0.      1.      0.    ]
     [ 0.      0.      0.      1.    ]
     [-1.4     1.2    -0.0058  0.0014]
     [ 0.8    -1.4     0.0016 -0.0038]]
    >>> print('B: ', B)
    B:  [[ 0.]
     [ 0.]
     [ 0.]
     [ 1.]]
    >>> print('C: ', Css)
    C:  [[-1.4     1.2    -0.0058  0.0014]]
    >>> print('D: ', D)
    D:  [[-0.2]]
    """

    A = np.vstack((np.hstack((np.zeros_like(M), np.eye(M.shape[0]))),
                   np.hstack((-la.solve(M, K), -la.solve(M, C)))))
    B = np.vstack((np.zeros((Bt.shape[0], 1)), Bt))
    C_ss = np.hstack((Cd - Ca@la.solve(M, K), Cv - Ca@la.solve(M, C)))
    D = Ca@la.solve(M, Bt)

    return A, B, C_ss, D


def damp(A):
    '''Display natural frequencies and damping ratios of state matrix.
    '''

    # Original Author: Kai P. Mueller <mueller@ifr.ing.tu-bs.de> for Octave
    # Created: September 29, 1997.

    print("............... Eigenvalue ...........     Damping     Frequency")
    print("--------[re]---------[im]--------[abs]----------------------[Hz]")
    e, _ = la.eig(A)

    for i in range(len(e)):
        pole = e[i]

        d0 = -np.cos(math.atan2(np.imag(pole), np.real(pole)))
        f0 = 0.5 / np.pi * abs(pole)
        if (abs(np.imag(pole)) < abs(np.real(pole))):
            print('      {:.3f}                    {:.3f}       \
                  {:.3f}         {:.3f}'.format(float(np.real(pole)),
                  float(abs(pole)), float(d0), float(f0)))

        else:
            print('      {:.3f}        {:+.3f}      {:.3f}       \
                  {:.3f}         {:.3f}'.format(float(np.real(pole)),
                  float(np.imag(pole)), float(abs(pole)), float(d0),
                  float(f0)))

def undamped_modes(M,K):
    '''Undamped modes and natural frequencies from Mass and Stiffness matrix.

    Parameters
    ----------
    M, K : float arrays
        Mass and stiffness matrices

    Returns
    -------
    omega : float array (1xN)
        Vector of natural frequencies (rad/sec)
    Psi : float array (NxN)
        Matrix of mass normalized mode shapes by column

    Examples
    --------
    >>> import numpy as np
    >>> import vibrationtesting as vt
    >>> M = np.array([[4, 0, 0],
    ...               [0, 4, 0],
    ...               [0, 0, 4]])
    >>> K = np.array([[8, -4, 0],
    ...               [-4, 8, -4],
    ...               [0, -4, 4]])
    >>> omega, Psi = vt.undamped_modes(M, K)
    >>> print(omega)
    [ 0.445   1.247   1.8019]
    >>> print(Psi)
    [[ 0.164  -0.3685 -0.2955]
     [ 0.2955 -0.164   0.3685]
     [ 0.3685  0.2955 -0.164 ]]
    '''
    lam, psi_flipped = la.eigh(M, K)

    omega = np.real(np.sqrt(1/lam[-1::-1]))

    Psi = np.fliplr(psi_flipped)

    norms = np.diag(1/np.sqrt(np.diag(Psi.T@M@Psi)))

    Psi = Psi @ norms

    return omega, Psi






