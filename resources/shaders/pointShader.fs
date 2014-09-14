#version 330

in vec4 vout_color;
out vec4 fout_color;

void main(void)
{
    fout_color = vout_color;
}