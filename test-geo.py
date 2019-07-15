from __future__ import print_function
import fitz
import sys
import time

mytime = time.clock if str is bytes else time.perf_counter
bitness = "64 bit" if sys.maxsize > 2 ** 32 else "32 bit"

print("Python:", sys.version, bitness, "on", sys.platform, "\n")
print(fitz.__doc__)

alpha = 255
m1 = fitz.Matrix(alpha)
m2 = fitz.Matrix(-alpha)
m3 = m1 * m2
print()
print("Checking 'Matrix(%i) * Matrix(-%i) == Identity'." % (alpha, alpha))
print("Deviation: %g" % abs(m3 - fitz.Identity))

repeats = 10000
t0 = mytime()
for i in range(repeats):
    m3 = m1 * m2
t1 = mytime()
quot = (t1 - t0) / repeats
print("Average multiplication time: %g sec" % quot)

print(" Point & Rectangle Tests ".center(80, "="))
p1 = fitz.Point(10, 20)
p2 = fitz.Point(100, 200)
p3 = fitz.Point(150, 250)
r = fitz.Rect(10, 20, 100, 200)
print("r =", r)
print("p1 =", p1)
print("p2 =", p2)
print("p3 =", p3)
print("fitz.Rect(p1,p2) =", fitz.Rect(p1, p2))
print("fitz.Rect(p1, 100, 200) =", fitz.Rect(p1, 100, 200))
print("fitz.Rect(10, 20, p2) =", fitz.Rect(10, 20, p2))
print("r.includePoint(p3) =", r.includePoint(p3))
r = fitz.Rect(10, 20, 100, 200)
print("r.includeRect((100,200,110,220)) =", r.includeRect((100, 200, 110, 220)))
print("include an empty rectangle: no change")
print("r.includeRect((0, 0, 0, 0)) =", r.includeRect((0, 0, 0, 0)))
print("include an infinite rectangle: infinite")
print("r.includeRect((1, 1, -1, -1)) =", r.includeRect((1, 1, -1, -1)))
print("")
print(" Matrix Tests ".center(80, "="))

m45p = fitz.Matrix(45)
m45m = fitz.Matrix(-45)
m90 = fitz.Matrix(90)
print("All of the following should be (close to) zero:")
print("|rot(90) - rot(45)*rot(45)| =", abs(m90 - m45p * m45p))
print("|rot(45)*rot(-45) - Id| =", abs(fitz.Identity - m45p * m45m))
print("|rot(45) - inv(rot(-45))| =", abs(m45p - ~m45m))
