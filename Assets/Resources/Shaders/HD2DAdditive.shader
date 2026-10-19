// Luz somada: brilhos, halos de lâmpada, partículas, a luz do relógio.
Shader "Joaquim/HD2D/Additive"
{
    Properties
    {
        _MainTex ("Textura", 2D) = "white" {}
        _Color ("Cor", Color) = (1,1,1,1)
        _Flip ("Espelhar", Float) = 0
    }
    SubShader
    {
        Tags { "Queue"="Transparent+10" "RenderType"="Transparent" "IgnoreProjector"="True" }
        Blend One One
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
            float _Flip;

            struct v2f { float4 pos : SV_POSITION; float2 uv : TEXCOORD0; };

            v2f vert (appdata_base v)
            {
                v2f o;
                o.pos = UnityObjectToClipPos(v.vertex);
                float2 uv = v.texcoord.xy;
                uv.x = lerp(uv.x, 1.0 - uv.x, _Flip);
                o.uv = uv;
                return o;
            }

            fixed4 frag (v2f i) : SV_Target
            {
                fixed4 t = tex2D(_MainTex, i.uv);
                return fixed4(t.rgb * t.a * _Color.rgb * _Color.a, 1);
            }
            ENDCG
        }
    }
}
