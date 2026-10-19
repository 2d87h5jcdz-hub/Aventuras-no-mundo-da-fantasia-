// Pós-processamento estilo HD-2D: desfoque de profundidade, bloom, raios de sol,
// correção de cor e vinheta. Usado por HD2DPost.cs (OnRenderImage).
Shader "Hidden/Joaquim/HD2DPost"
{
    Properties
    {
        _MainTex ("", 2D) = "white" {}
    }

    CGINCLUDE
    #include "UnityCG.cginc"

    sampler2D _MainTex;
    float4 _MainTex_TexelSize;
    sampler2D _BlurTex;
    sampler2D _BloomTex;
    UNITY_DECLARE_DEPTH_TEXTURE(_CameraDepthTexture);

    float4 _BlurDir;
    float _Threshold;
    float _FocusDist;
    float _DofStrength;
    float _DofMax;
    float _BloomIntensity;
    float4 _BloomTint;
    float _Vignette;
    float _Saturation;
    float _Contrast;
    float4 _ShadowTint;
    float4 _Grade;
    float _RaysIntensity;
    float _RaysAngle;
    float4 _RaysColor;

    struct v2f
    {
        float4 pos : SV_POSITION;
        float2 uv : TEXCOORD0;
    };

    v2f vert (appdata_img v)
    {
        v2f o;
        o.pos = UnityObjectToClipPos(v.vertex);
        o.uv = v.texcoord;
        return o;
    }

    float4 fragPrefilter (v2f i) : SV_Target
    {
        float3 c = tex2D(_MainTex, i.uv).rgb;
        float l = max(c.r, max(c.g, c.b));
        float k = saturate((l - _Threshold) / max(1e-4, 1.0 - _Threshold));
        return float4(c * k, 1);
    }

    float4 fragBlur (v2f i) : SV_Target
    {
        float2 d = _BlurDir.xy * _MainTex_TexelSize.xy;
        float3 c = tex2D(_MainTex, i.uv).rgb * 0.227027;
        c += tex2D(_MainTex, i.uv + d * 1.3846).rgb * 0.316216;
        c += tex2D(_MainTex, i.uv - d * 1.3846).rgb * 0.316216;
        c += tex2D(_MainTex, i.uv + d * 3.2308).rgb * 0.070270;
        c += tex2D(_MainTex, i.uv - d * 3.2308).rgb * 0.070270;
        return float4(c, 1);
    }

    float hash1 (float n) { return frac(sin(n) * 43758.5453); }

    float noise1 (float x)
    {
        float i = floor(x);
        float f = frac(x);
        f = f * f * (3.0 - 2.0 * f);
        return lerp(hash1(i), hash1(i + 1.0), f);
    }

    float4 fragComposite (v2f i) : SV_Target
    {
        float3 sharp = tex2D(_MainTex, i.uv).rgb;
        float3 blur = tex2D(_BlurTex, i.uv).rgb;

        // profundidade de campo: quanto mais longe do foco, mais desfoque
        float raw = SAMPLE_DEPTH_TEXTURE(_CameraDepthTexture, i.uv);
        float d = LinearEyeDepth(raw);
        float coc = saturate(abs(1.0 / d - 1.0 / _FocusDist) * _DofStrength);
        coc = min(coc, _DofMax);
        float3 c = lerp(sharp, blur, coc);

        // bloom
        c += tex2D(_BloomTex, i.uv).rgb * _BloomIntensity * _BloomTint.rgb;

        // raios de sol diagonais
        float2 p = i.uv * 2.0 - 1.0;
        p.x *= _ScreenParams.x / _ScreenParams.y;
        float proj = p.x * cos(_RaysAngle) + p.y * sin(_RaysAngle);
        float r = noise1(proj * 7.0 + _Time.y * 0.04);
        r = r * r * r;
        r *= saturate((p.y + 0.2) / 1.2);
        c += _RaysColor.rgb * r * _RaysIntensity;

        // cor
        c *= _Grade.rgb;
        float l = dot(c, float3(0.299, 0.587, 0.114));
        c = lerp(float3(l, l, l), c, _Saturation);
        c = (c - 0.5) * _Contrast + 0.5;
        float sh = 1.0 - saturate(l);
        c += _ShadowTint.rgb * sh * sh;

        // vinheta
        float2 v = i.uv * 2.0 - 1.0;
        v.x *= 0.9;
        float vig = pow(saturate(1.0 - dot(v, v) * _Vignette), 1.3);
        c *= vig;

        return float4(saturate(c), 1);
    }
    ENDCG

    SubShader
    {
        Cull Off ZWrite Off ZTest Always

        Pass // 0: só o que é bem claro (para o bloom)
        {
            CGPROGRAM
            #pragma vertex vert
            #pragma fragment fragPrefilter
            ENDCG
        }
        Pass // 1: desfoque gaussiano numa direção
        {
            CGPROGRAM
            #pragma vertex vert
            #pragma fragment fragBlur
            ENDCG
        }
        Pass // 2: junta tudo
        {
            CGPROGRAM
            #pragma vertex vert
            #pragma fragment fragComposite
            ENDCG
        }
    }
}
