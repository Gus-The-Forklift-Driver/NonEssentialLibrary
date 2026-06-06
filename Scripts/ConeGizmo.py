# This script creates a script that draws a cone gizmo in a debug view. The cone is defined by its forward direction, origin and radius.
print('//inputs')
print('//float3 Forward')
print('//float3 Origin')
print('//float Radius')
print('//bool Enabled')
print('//float4 ColorStart')
print('//float4 ColorEnd')

print('float radii = degrees.cos(Radius);')
print('float mul = sqrt(1-radii*radii);')
print('float len = length(Forward);')


print('Forward = normalize(Forward);')
print('float3 side = normalize(iif(cross(Forward,float3(1,0,0)),cross(Forward,float3(1,0,0)),(abs(dot(Forward,float3(1,0,0)))>0.9)));')
print('float3 side2 = normalize(cross(side,Forward));')

count = 8

for i in range(count):
    angle = (i / count) * 3.1415926 * 2.0
    print(f'float3 v{i} = Origin + len*(Forward * radii + side * radians.cos(({i+1}.f / {count}.f) * pi * 2.0f) * mul + side2 * radians.sin(({i+1}.f / {count}.f) * pi * 2.0f) * mul);')

for i in range(count):
    print(f'debug.drawLine(Enabled, Origin, v{i}, ColorStart, ColorEnd);')
    print(f'debug.drawLine(Enabled, v{(i-1) % count}, v{i}, ColorEnd, ColorEnd);')
