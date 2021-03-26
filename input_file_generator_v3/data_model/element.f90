module Element_mod
!
!  Data base of chemical elements with service routines
!
!  Used Modules:
!  ============
!
   use Const_mod, only: REAL8, INT4,  &
                        ZERO, ONE
!
!  Default Type and Access:
!  =======================
!
   implicit none
   private
   save
!
!  Public Procedures:
!  =================
!
   public :: anaMolecule            ! analyse molecule name and return atom name, atomic
!            ===========            !    number, and abundance
   public :: getElemName            ! get the name of the element
!            ===========
   public :: getIonMass             ! get the mass of the most abundant isotope
!            ==========
   public :: getTargetMass          ! get average mass of atom in a solid target
!            =============
   public :: getDens                ! get atomic density of monoatomic target
!            =======
   public :: getDebyeTemp           ! get Debye temperature of atom
!            ============
   public :: getEsurf               ! get the surface binding energy
!            ========
!
!  Private Data:
!  ============
!
   type :: Elem_type                         ! chemical element data type
!          =========
      character(2) :: name
      real(REAL8) :: mass1
      real(REAL8) :: mass2
      real(REAL8) :: dens
      character(12) :: name1
      character(12) :: name2
      real(REAL8) :: tDebye
      real(REAL8) :: esurf
   end type Elem_type

   type(Elem_type) :: elem(92)

   data elem( 1: 2) / &
      Elem_type( 'H ',  1.0078, 1.008,  4.271,'HYDROGEN    ','HYDROGEN    ', 110. , 0.   ) , &
      Elem_type( 'HE',  4.0026, 4.0026, 1.894,'HELIUM      ','HELIUM      ',   0. , 0.   ) /
   data elem( 3:10) / &
      Elem_type( 'LI',  7.016,  6.939,  4.597,'LITHIUM     ','LITHIUM     ', 344. , 1.67 ) , &
      Elem_type( 'BE',  9.012,  9.0122,12.046,'BERYLLIUM   ','BERYLLIUM   ',1440. , 3.38 ) , &
      Elem_type( 'B ', 11.009, 10.811, 13.093,'BORON       ','BORON       ',1250. , 5.73 ) , &
      Elem_type( 'C ', 12.   , 12.011, 11.364,'CARBON      ','CARBON      ',2230. , 7.41 ) , &
      Elem_type( 'N ', 14.003, 14.007, 22.59 ,'NITROGEN    ','NITROGEN    ',   0. , 0.   ) , &  ! density=3.481, but 22.59 gives the correct density of Si3N4
      Elem_type( 'O ', 15.995, 15.999,  8.759,'OXYGEN      ','OXYGEN      ',   0. , 0.   ) , &  ! density=4.302, but 8.759 gives correct density of SiO2
      Elem_type( 'F ', 18.998, 18.998,  3.522,'FLUORINE    ','FLUORINE    ',   0. , 0.   ) , &
      Elem_type( 'NE', 19.992, 20.183,  3.585,'NEON        ','NEON        ',  75. , 0.   ) /
   data elem(11:18) / &
      Elem_type( 'NA', 22.99 , 22.989,  2.541,'SODIUM      ','NATRIUM     ', 158. , 1.12 ) , &
      Elem_type( 'MG', 23.985, 24.312,  4.302,'MAGNESIUM   ','MAGNESIUM   ', 400. , 1.54 ) , &
      Elem_type( 'AL', 26.982, 26.981,  6.023,'ALUMINIUM   ','ALUMINUM    ', 428. , 3.36 ) , &
      Elem_type( 'SI', 27.977, 28.086,  4.994,'SILICON     ','SILICON     ', 493.6, 4.70 ) , &
      Elem_type( 'P ', 30.994, 30.973,  3.542,'PHOSPHORUS  ','PHOSPHORUS  ',   0. , 3.27 ) , &
      Elem_type( 'S ', 31.97 , 32.064,  3.885,'SULFUR      ','SULFUR      ',   0. , 2.88 ) , &
      Elem_type( 'CL', 34.969, 35.453,  3.22 ,'CHLORINE    ','CHLORINE    ',   0. , 0.   ) , &
      Elem_type( 'AR', 39.98 , 39.948,  2.488,'ARGON       ','ARGON       ',  92. , 0.   ) /
   data elem(19:36) / &
      Elem_type( 'K ', 38.96 , 39.102,  1.329,'POTASSIUM   ','KALIUM      ',  91. , 0.93 ) , &
      Elem_type( 'CA', 39.96 , 40.08 ,  2.014,'CALCIUM     ','CALCIUM     ', 230. , 1.83 ) , &
      Elem_type( 'SC', 44.956, 44.956,  4.015,'SCANDIUM    ','SCANDIUM    ', 360. , 3.49 ) , &
      Elem_type( 'TI', 47.95 , 47.9  ,  5.682,'TITANIUM    ','TITANIUM    ', 420. , 4.89 ) , &
      Elem_type( 'V ', 50.94 , 50.942,  7.213,'VANADIUM    ','VANADIUM    ', 380. , 5.33 ) , &
      Elem_type( 'CR', 51.94 , 51.996,  8.33 ,'CHROMIUM    ','CHROMIUM    ', 630. , 4.12 ) , &
      Elem_type( 'MN', 54.94 , 54.938,  8.15 ,'MANGANESE   ','MANGANESE   ', 410. , 2.98 ) , &
      Elem_type( 'FE', 55.94 , 55.847,  8.483,'IRON        ','IRON        ', 470. , 4.34 ) , &
      Elem_type( 'CO', 58.93 , 58.933,  8.989,'COBALT      ','COBALT      ', 445. , 4.43 ) , &
      Elem_type( 'NI', 57.94 , 58.71 ,  9.125,'NICKEL      ','NICKEL      ', 450. , 4.46 ) , &
      Elem_type( 'CU', 62.93 , 63.54 ,  8.483,'COPPER      ','COPPER      ', 343. , 3.52 ) , &
      Elem_type( 'ZN', 63.93 , 65.37 ,  6.546,'ZINC        ','ZINC        ', 327. , 1.35 ) , &
      Elem_type( 'GA', 68.93 , 69.72 ,  5.104,'GALLIUM     ','GALLIUM     ', 320. , 2.82 ) , &
      Elem_type( 'GE', 73.92 , 72.59 ,  4.428,'GERMANIUM   ','GERMANIUM   ', 374. , 3.88 ) , &
      Elem_type( 'AS', 74.92 , 74.922,  4.597,'ARSENIC     ','ARSENIC     ', 282. , 1.26 ) , &
      Elem_type( 'SE', 79.92 , 78.96 ,  3.65 ,'SELENIUM    ','SELENIUM    ',  90. , 2.14 ) , &
      Elem_type( 'BR', 78.92 , 79.909,  2.562,'BROMINE     ','BROMINE     ',   0. , 0.   ) , &
      Elem_type( 'KR', 83.92 , 83.8  ,  1.87 ,'KRYPTON     ','KRYPTON     ',  72. , 0.   ) /
   data elem(37:54) / &
      Elem_type( 'RB', 84.91 , 85.47 ,  1.077,'RUBIDIUM    ','RUBIDIUM    ',  56. , 0.86 ) , &
      Elem_type( 'SR', 87.91 , 87.62 ,  1.787,'STRONTIUM   ','STRONTIUM   ', 147. , 1.70 ) , &
      Elem_type( 'Y ', 89.91 , 88.905,  3.041,'YTTRIUM     ','YTTRIUM     ', 280. , 4.24 ) , &
      Elem_type( 'ZR', 89.9  , 91.22 ,  4.271,'ZIRCONIUM   ','ZIRCONIUM   ', 291. , 6.33 ) , &
      Elem_type( 'NB', 92.91 , 92.906,  5.576,'NIOBIUM     ','NIOBIUM     ', 275. , 7.59 ) , &
      Elem_type( 'MO', 95.5  , 95.94 ,  6.407,'MOLYBDENUM  ','MOLYBDENUM  ', 450. , 6.83 ) , &
      Elem_type( 'TC',  0.   ,  99.  ,  0.   ,'TECHNETIUM  ','TECHNETIUM  ', 453. , 0.   ) , &
      Elem_type( 'RU',101.9  ,101.07 ,  7.256,'RUTHENIUM   ','RUTHENIUM   ', 600. , 6.69 ) , &
      Elem_type( 'RH',102.9  ,102.91 ,  7.256,'RHODIUM     ','RHODIUM     ', 480. , 5.78 ) , &
      Elem_type( 'PD',105.9  ,106.4  ,  6.767,'PALLADIUM   ','PALLADIUM   ', 274. , 3.91 ) , &
      Elem_type( 'AG',106.9  ,107.87 ,  5.847,'SILVER      ','SILVER      ', 225. , 2.97 ) , &
      Elem_type( 'CD',113.9  ,112.4  ,  4.597,'CADMIUM     ','CADMIUM     ', 209. , 1.16 ) , &
      Elem_type( 'IN',114.9  ,114.82 ,  3.836,'INDIUM      ','INDIUM      ', 108. , 2.49 ) , &
      Elem_type( 'SN',119.9  ,118.69 ,  3.695,'TIN         ','TIN         ', 200. , 3.12 ) , &
      Elem_type( 'SB',120.9  ,121.75 ,  3.273,'ANTIMONY    ','STIBIUM     ', 211. , 2.72 ) , &
      Elem_type( 'TE',130.   ,127.6  ,  2.938,'TELLURIUM   ','TELLURIUM   ', 153. , 2.02 ) , &
      Elem_type( 'J ',126.9  ,126.9  ,  2.343,'IODINE      ','IODINE      ',   0. , 0.   ) , &
      Elem_type( 'XE',129.5  ,131.3  ,  1.403,'XENON       ','XENON       ',  64. , 0.   ) /
   data elem(55:86) / &
      Elem_type( 'CS',134.   ,132.91 ,  0.86 ,'CAESIUM     ','CAESIUM     ',  38. , 0.81 ) , &
      Elem_type( 'BA',138.   ,137.34 ,  1.544,'BARIUM      ','BARIUM      ', 110. , 1.84 ) , &
      Elem_type( 'LA',139.   ,138.91 ,  2.676,'LANTHANUM   ','LANTHANUM   ', 142. , 4.42 ) , &
      Elem_type( 'CE',140.   ,140.12 ,  2.868,'CERIUM      ','CERIUM      ',   0. , 4.23 ) , &
      Elem_type( 'PR',141.   ,140.91 ,  2.895,'PRASEODYMIUM','PRASEODYMIUM',   0. , 3.71 ) , &
      Elem_type( 'ND',142.   ,144.24 ,  2.932,'NEODYMIUM   ','NEODYMIUM   ',   0. , 3.28 ) , &
      Elem_type( 'PM',  0.   ,147.   ,  0.   ,'PROMETHIUM  ','PROMETHIUM  ',   0. , 0.   ) , &
      Elem_type( 'SM',152.   ,150.35 ,  3.026,'SAMARIUM    ','SAMARIUM    ', 166. , 2.16 ) , &
      Elem_type( 'EU',153.   ,151.96 ,  2.084,'EUROPIUM    ','EUROPIUM    ',   0. , 1.85 ) , &
      Elem_type( 'GD',157.9  ,157.25 ,  3.026,'GADOLINIUM  ','GADOLINIUM  ', 200. , 3.57 ) , &
      Elem_type( 'TB',159.9  ,158.92 ,  3.136,'TERBIUM     ','TERBIUM     ',   0. , 3.81 ) , &
      Elem_type( 'DY',164.   ,162.5  ,  3.17 ,'DYSPROSIUM  ','DYSPROSIUM  ', 210. , 2.89 ) , &
      Elem_type( 'HO',165.   ,164.93 ,  3.22 ,'HOLMIUM     ','HOLMIUM     ',   0. , 3.05 ) , &
      Elem_type( 'ER',166.   ,167.26 ,  3.273,'ERBIUM      ','ERBIUM      ',   0. , 3.05 ) , &
      Elem_type( 'TM',169.   ,168.93 ,  3.327,'THULIUM     ','THULIUM     ',   0. , 2.52 ) , &
      Elem_type( 'YB',174.   ,173.04 ,  2.428,'YTTERBIUM   ','YTTERBIUM   ', 120. , 1.74 ) , &
      Elem_type( 'LU',175.   ,174.97 ,  3.383,'LUTETIUM    ','LUTETIUM    ', 210. , 4.29 ) , &
      Elem_type( 'HF',180.   ,178.49 ,  4.428,'HAFNIUM     ','HAFNIUM     ', 252. , 6.31 ) , &
      Elem_type( 'TA',181.   ,180.95 ,  5.525,'TANTALUM    ','TANTALUM    ', 240. , 8.10 ) , &
      Elem_type( 'W ',184.   ,183.85 ,  6.32 ,'TUNGSTEN    ','WOLFRAM     ', 400. , 8.68 ) , &
      Elem_type( 'RE',187.   ,186.2  ,  6.805,'RHENIUM     ','RHENIUM     ', 430. , 8.09 ) , &
      Elem_type( 'OS',192.   ,190.2  ,  7.144,'OSMIUM      ','OSMIUM      ', 500. , 8.13 ) , &
      Elem_type( 'IR',193.   ,192.2  ,  7.052,'IRIDIUM     ','IRIDIUM     ', 420. , 6.90 ) , &
      Elem_type( 'PT',195.   ,195.09 ,  6.618,'PLATINUM    ','PLATINUM    ', 240. , 5.86 ) , &
      Elem_type( 'AU',197.   ,196.97 ,  5.904,'GOLD        ','GOLD        ', 165. , 3.80 ) , &
      Elem_type( 'HG',202.   ,200.59 ,  4.069,'MERCURY     ','MERCURY     ',  71.9, 0.64 ) , &
      Elem_type( 'TL',205.   ,204.37 ,  3.501,'THALLIUM    ','THALLIUM    ',  78.5, 1.88 ) , &
      Elem_type( 'PB',208.   ,207.19 ,  3.291,'LEAD        ','LEAD        ', 105. , 2.03 ) , &
      Elem_type( 'BI',209.   ,208.98 ,  2.827,'BISMUTH     ','BISMUTH     ', 119. , 2.17 ) , &
      Elem_type( 'PO',210.   ,210.   ,  2.653,'POLONIUM    ','POLONIUM    ',   0. , 1.50 ) , &
      Elem_type( 'AT',210.   ,210.   ,  0.   ,'ASTATINE    ','ASTATINE    ',   0. , 0.   ) , &
      Elem_type( 'RN',222.   ,222.   ,  0.   ,'RADON       ','RADON       ',   0. , 0.   ) /
   data elem(87:92) / &
      Elem_type( 'FR',223.   ,223.   ,  0.   ,'FRANCIUM    ','FRANCIUM    ',   0. , 0.   ) , &
      Elem_type( 'RA',226.   ,226.   ,  1.338,'RADIUM      ','RADIUM      ',   0. , 0.   ) , &
      Elem_type( 'AC',227.   ,227.   ,  0.   ,'ACTINIUM    ','ACTINIUM    ',   0. , 0.   ) , &
      Elem_type( 'TH',232.   ,232.   ,  3.026,'THORIUM     ','THORIUM     ', 163. , 5.93 ) , &
      Elem_type( 'PA',231.   ,231.   ,  4.015,'PROTACTINIUM','PROTACTINIUM', 0.   , 0.   ) , &
      Elem_type( 'U ',238.04 ,238.04 ,  4.818,'URANIUM     ','URANIUM     ', 207. , 5.42 ) /
!
   character(52) :: alf = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
   character(10) :: num = '1234567890'
!
contains
!
!=======================================================================
!
   subroutine anaMolecule( molec, ele, iz, nabund )
!             ===========   io     o   o     o
!
!     Analyze the molecule name and extract the name, atomic number, and
!     abundance of the first atom referenced. Return the molecule name minus
!     the first atom.
!
!  Arguments:
!
      character(*), intent(inout) :: molec      ! chemical name of the molecule
      character(2), intent(out) :: ele          ! chemical name of the atom
      integer(INT4), intent(out) :: iz          ! atomic number
      integer(INT4), intent(out) :: nabund      ! abundance of atom in molecule
!
!  Local Variables:
!
      integer(INT4) :: k, i
!
!  Start of Executable Code:
!  ------------------------
!
      ele = ' '
      iz = 0
      nabund = 0
!
!  Skip leading blanks
!
      do k = 1, len(molec)
         if( molec(k:k) /= ' '  )  exit
      enddo
      if( k > len(molec) ) return
!
!  Get element name
!
      i = index( alf, molec(k:k) )
      if( i == 0 )  return                        ! no letter
      if( i > 26 )  i = i - 26                    ! convert to uppercase
      ele = alf(i:i)

      k = k + 1                                 ! test second letter
      if( k > len(molec) ) return
      i = index( alf, molec(k:k) )
      if( i > 0 ) then                           ! if there is a second letter, assign it
         if( i > 26)  i = i - 26                 !    to the element name preliminarly
         ele(2:2) = alf(i:i)
         k = k + 1
      endif
!
!  Search for the element name in the list
!
      do i = 1, 92
         if( ele == elem(i)%name )  exit
      enddo
                                                ! the second letter could belong to the next
                                                !    element; if element has not been found,
      if( i > 92 .and. ele(2:2) /= ' ' ) then    !    try one-character name
         ele(2:2) = ' '
         k = k - 1
         do i = 1, 92
            if( ele == elem(i)%name )  exit
         enddo
      endif

      if( i > 92 )  stop 'invalid ion species or target material'

      iz = i                                    ! element name found => ele, iz
!
!  Get abundance of the atom in the molecule
!
      if( k > len(molec) ) then                  ! if at end of molecule name ...
         nabund = 1
      else if( index(num,molec(k:k)) == 0 ) then ! if next character is a letter ...
         nabund = 1
      else                                      ! otherwise (next character a digit) ...
         do
            read( molec(k:k),'(i1)' ) i
            nabund = 10 * nabund + i
            k = k + 1
            if( k > len(molec) )  exit
            if( index( num, molec(k:k) ) == 0 )  exit
         end do
      end if

      molec = molec(k:len(molec))

   end subroutine anaMolecule
!
!=======================================================================
!
   subroutine getElemName( iz, name )
!             ===========  i    o
!
!     Get the name of the element
!
!  Arguments:
!
      integer(INT4), intent(in) :: iz           ! atomic number
      character(2), intent(out) :: name         ! element name
!
!  Local Variables:
!
!     none
!
!  Start of Executable Code:
!  ------------------------
!
      name = elem(iz)%name

   end subroutine getElemName
!
!=======================================================================
!
   subroutine getIonMass( iz, m )
!             ==========  i   o
!
!     Get the mass of the most abundant isotope
!
!  Arguments:
!
      integer(INT4), intent(in) :: iz           ! atomic number
      real(REAL8), intent(out) :: m             ! ion mass [amu]
!
!  Local Variables:
!
!     none
!
!  Start of Executable Code:
!  ------------------------
!
      m = elem(iz)%mass1

   end subroutine getIonMass
!
!=======================================================================
!
   subroutine getTargetMass( iz, m )
!             =============  i   o
!
!     Get the average mass of the atom in a solid target
!
!  Arguments:
!
      integer(INT4), intent(in) :: iz           ! atomic number
      real(REAL8), intent(out) :: m             ! average atom mass [amu]
!
!  Local Variables:
!
!     none
!
!  Start of Executable Code:
!  ------------------------
!
      m = elem(iz)%mass2

   end subroutine getTargetMass
!
!=======================================================================
!
   subroutine getDens( iz, dens )
!             =======  i    o
!
!     Get the mass of the most abundant isotope
!
!  Arguments:
!
      integer(INT4), intent(in) :: iz           ! atomic number
      real(REAL8), intent(out) :: dens          ! atom density [1/A^3]
!
!  Local Variables:
!
!     none
!
!  Start of Executable Code:
!  ------------------------
!
      dens = elem(iz)%dens * 1e-2
      if( dens == 0 )  stop 'No density defined for element'

   end subroutine getDens
!
!=======================================================================
!
   subroutine getDebyeTemp( iz, tdebye )
!             ============  i      o
!
!     Get the Debye temperature of the atom
!
!  Arguments:
!
      integer(INT4), intent(in) :: iz           ! atomic number
      real(REAL8), intent(out) :: tdebye        ! Debye temperature [K]
!
!  Local Variables:
!
!     none
!
!  Start of Executable Code:
!  ------------------------
!
      tdebye = elem(iz)%tDebye

   end subroutine getDebyeTemp
!
!=======================================================================
!
   subroutine getEsurf( iz, esurf )
!             ========  i     o
!
!     Get the surface binding energy of the pure element
!
!  Arguments:
!
      integer(INT4), intent(in) :: iz           ! atomic number
      real(REAL8), intent(out) :: esurf         ! surface binding energy [eV]
!
!  Local Variables:
!
!     none
!
!  Start of Executable Code:
!  ------------------------
!
      esurf = elem(iz)%esurf

   end subroutine getEsurf
!
!=======================================================================
!
end module Element_mod
