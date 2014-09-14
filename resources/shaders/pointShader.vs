#version 330

uniform mat4 WVP;

in vec3 vin_position;
in vec4 vin_color;
smooth out vec4 vout_color;

void main(void)
{
    vout_color = vin_color;
    gl_Position = WVP * vec4(vin_position, 1.0);
}