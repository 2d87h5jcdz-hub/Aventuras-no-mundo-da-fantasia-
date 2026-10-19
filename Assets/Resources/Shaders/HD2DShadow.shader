// Sombra no chão: multiplica o que está embaixo por uma cor escura.
Shader "Joaquim/HD2D/Shadow"
{
    Properties
    {
        _MainTex ("Textura", 2D) = "white" {}
        _Color ("Cor da sombra (a = força)", Color) = (0.2,0.15,0.3,0.6)
        _Flip ("Espelhar", Float) = 0
    }
    SubShader
    {
        Tags { "Queue"="Transparent-50" "RenderType"="Transparent" "IgnoreProjector"="True" }
        Blend DstColor Zero
        ZWrite Off
        Cull Off

        Pass
        {
            CGPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #include "UnityCG.cginc"

            sampler2D _MainTex;
            fixed4 _Color;

            struct v2f { float4 pos : SV_POSITION; float2 uv : TEXCOORD0; };

            v2f vert (appdata_base v)
            {
                v2f o;
                o.pos = UnityObjectToClipPos(v.vertex);
                o.uv = v.texcoord.xy;
                return o;
            }

            fixed4 frag (v2f i) : SV_Target
            {
                fixed a = tex2D(_MainTex, i.uv).a * _Color.a;
                return fixed4(lerp(fixed3(1,1,1), _Color.rgb, a), 1);
            }
            ENDCG
        }
    }
}
