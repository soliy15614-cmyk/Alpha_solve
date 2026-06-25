#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys

_V = [[60, 63, 45, 59, 104, 106], [36, 50, 55, 60], [29, 44, 39, 46, 42, 49, 112, 29, 55, 46, 54, 59, 44, 112, 31, 27, 13], [31, 27, 13], [43, 48, 46, 63, 58], [59, 38, 59, 61], [60, 102, 107, 58, 59, 61, 49, 58, 59], [60, 104, 106, 58, 59, 61, 49, 58, 59], [48, 59, 41]]
_K = [94]

def _x(n):
    return "".join(chr(x ^ _K[0]) for x in _V[n])

def _run():
    _e = "qa9n0E0J?-JqzHH<KID%BO5RpzC~ChmC7a$IbrHd*k)wH#nWK_SpEM<VE=pNqeFWZeG~p68Svpfd-NjN-lyM~0op*xQc-;dW^w)2h7r+k<8cW`w)|Qm5#JKd8${>nG*MSc1<0mbhCjUnN)Xg4(F9s2*O{!_v=Mp%SX~KYsnr8R)xS@)G)-bDuA9{+>0>sw_@;>jKD)6iG$evPawLO$xi=nCu<|{0{rqZ6$`d-TdYDDESN_>#>B~p!E2_M^EUDi?lcWL)H*rr**wJY_qfQG(pO8`@7BH=_HQu3OeFaCwyW1I|<|S%mYHbZ*g}-UOGiKZ^k8L_}!%1O;nsy{p_E2fe5NT@2hp=V}Q&*g9IqgAJi5hc?9IfBv@?`p3{Zl6#V1{oY_qERUXMuE_ygo%FO7JG+>`KOfVaq~*y5xA9rv<i=hkSdeWxK?q2k;#i8;NOvJP;Ud?((YNM5^Y?Q`0Ii)U*U>ddm6SNPd?-+qx_`ZL8Q92{%wA0Z6pzEhC<|c&=i}Z>Qr@c4I0)1${6OZer-#GY)R-u1hKF#Ni#!+0$V~FumHQ^yRP(`6o<wfz-QG8|Eb@*_KV7F>eTT_~g*nK~6jR?#LeIVFnO5^An*(-35%;=#ArHD93946Sv1e4*~*W-Lj$oG0+KUh0E=F3)P=5i0e7o76NKQ4hnj`xTJALRVK7M`L&XtgO_}Rj6B_3ntA0qZ9F1dA_A5d=mATqRwLYfazC-f2j*E#&F_^CUWc$YR6Y1&O_$kiRYf7|8zR<xm;(WWs?db8C=Wlka(Gu`!LAF2Wn82<wQ^Whuc@18bPTCIPejV^qf^SG_F-rk%RPGVHTK^b6zxEF6KYF0BW?4(t@!oWtWu~($GiJ4V#t^e^lf#>eR1$zfmB*5DNKkF<I*NYSP0B4J<hV7+~9hej(_P%%t<v#SE_&JvZCWvkLx8@!+nIBh>(KY-b8*p;js({cZ&<?VkXGOc$Pp_>-6w0a|r-!5Jf}Q#^E)}#H0F_yQ`FI<{kDlQuMJLliM+O<h?hV@Q^n(vcXY$=wG1Xe1=((gzmyLE$pV3D*kw#LV>(EiMEf<i9?v%Jxtx3uvv+H1RaPh$NON{?uoa!PE4C1d8F}#6g1c|w&6+B%xEMMzu1N_SmDhC&xuE_Nqbb)VQT#5z*!>b-NcPv_%pJAfgKr>vdc0G_E6{u17;SCS<^H5UG9Nw<koKF^TK?kF2Xmv@mn3z=bRdC$*Q>a&_#>&OIb}FD|w{M(-BAlOxQh~4c2FKa<PA@QJlqkqQfWJ2E8wU0^g1XePR-9Rro!h01f)#y|031?AHste(_5^NUB;^Q=|LY9pHZ>13Zfa5$cfzK(A7CgQ-aq?IBtlC<nSnid5a+svz_!SKYZVvCfsr0qv?dh#8wyS1SjnQG8u3t$7Kho@#rF#k3Wn4$zx5L#Dzt@`eKRN7NKe$;ftWf!wuQIN6W#b4c95gqdb>7T2f{5b5`ti&PQFW`v1$01^42RV720WXDiRs7@;(q<!XT_RUYRylYnLEkY6H6p2f+V#mG&`_MJe!e^Qr7EYvJFhtUd701xO>AZ{PP6aE)|2cWIchQHJ4RZl=;FMvm;u&a2zVZ8pW)cT466#@D{%R$qa!QbQ!S7I}o5rbB4lFrr^%#N7LW$k$9)Iah9a3{93)WMERgs07I+Gyf+*};p2Q3fkQZ`|0f|437|51Eo1A<b|d}JfV?4kI#Frot}J<{q8%bCAXbNVboE?)z@pYf7^_pHLe?ZVAylJ$P)y^Ri+KYdeJUN40!0b{x3OLh$YmFCvaENub`?Dr?2SitsIQ?*vpuI)ksVCrrHu-|_8P#hTSB`^RL@vZIxb!i%k+SL?|vr8YTQTTbRDhK*K#dT#mBkBiDaAH{QaQO1rEmYHc(9OB0l=3B6i(t!qP@%sWP7L<CM7d}ae5XhqC+9>1x*Qx>%*V+DS#SGM{^gBvd=QGCr?vRAYN|Zww;#-*yxcoM7hJo^ax^2mxSlcg1(N(ufM`FfM^9w>Ni_!cNd>v|iI1TljBn=enr_GhHlRFp5f0$ns40^z;^iIiD2FA2ZZaYzWw>@p`@eL_s(c&NOUP$rP(;ntj9@FAIOql8A=TDimi{`E?JXdEh7fJf_BNDOiOT<)592zo(A$3Wv8mVVdkqH$>u!N*T&Ubl>{wvmA9FPqO%D%*?g63UWO3Y|GFKCpjZ(y@!rZ|k8(TYAKXXBa15^EvWH>}6eE+pF@X8yP3tUNsUz8T22`6A<W{9a%0d!SK3?(jX9CP3lC>=T8)ExBXDw&9XEx$Js_|3Z}-dA<w=>3S)_#(=>0qolyWC&F#2NKOp36gqm;3=q*Z9OMR#QnF$Ni^B>$F5G~Dyo}nmBWYzcCI6~4k4Kt9BHd<qEY^W=`cjSgk@{;@%#N$`NUAzD3uIp!D(naIiycWCgBoH`7==()Y23)1W=6M#$Kds9vkL3gTC5U)f`YIE;Y3XWT$;ZG(kN2dBu>=Ht)Z8K>(Ooo2PMmLxtU9pd83$?Z3ie*VLOzId2XLbueUp27XF0l!GT9d&i0=Duq<$FZH*n#$J1jkHg93N9jj&@UL_9e3-j?6skF%6rMIA@^4sE;n6zX0Z-<fpJII`*$Q)XZk{s|5$ZUSCV@hE!;O5sr&tmNEe7IH9oH`@;6NwAEVmH`R=o<0B`haP8k+>h@!NUdm;peVLQYqw<Q2t{al_|>r9cDD1>k_|t{0$)w1SfX?Ui9LyGp=ED`8q8zD%)m{7~DKp@?#E$tvX<t2;ylZ?ssv+X<w=KD+6Vn1NCu^WOCr<X=KnOo*r0g<5O#l5alPYtOnVSWs70G_H(@qrF0(1D|d}!SvWuFLs2z;0btM;}yNE(Y&Xu)HmsK^FBaBTJ)3&t>SMuqxQVGua1?FGDxFC#PrqAY%D$%tEE|)&k}It5B!rD=7Z1C){B!G2kB!wvcmQtRNikFKK0)I8k7(=JeeJxmHKAHUz8W64h|7vJ3>wFq`9chEjkTt>m86iLs%>H-^?OV<0hP6qWDisjgKiOlWbJSlQui0Y(6oAB<f7^jQ#QC7c~kp4sT4u$Bo5vcsyIynk0JtLo|PPadYWD4fPZ%Xt*LlH5mW$$aB@boMN@U+UX?~PeI6y8_+udnzBLn{P;dmr3rY+@vE?JT~HyN$;IuN(d2>f%EB-bZ~sAFeRKXY`KLa=-NA-mW@$QbhQU%w&{{pzuf83>7!zxAi4mf*u@In2)F;2D$O>JMx{|?o`}Sw*^fDq)T9iI7Z!*4w`&2s{!VF*_f!0eA+G_BAzPcOa1x|8AF&keTk5EN}-M0ov;3H=xPie4637YO&d=G^8#tmQh?VE`W%IMnlbS5ZI$<T$^NZul)8giDOwKwqnCb#NLJjos^XdU-B`1~mzy40IK0P)UA;dL25?;x9nf8CF6cdRC}FFi;Ce6zV0;uM<rmNBp-nzo!vp8eR?E>qkUj`?0%D5(Wa;gvTB=|BJQUB$I)U40djCfKRlA)tMTAATTavNg>{B@rFjSsO)o03?0<o~wPfzu?|oUT_AE;RNN3g}M@1BN^?5y{V$SJ~DdjwoX@ZXIn{^`avxM{->iW7~9(4Hei3XaP#EMFm5}}K-(|V1&j{TJUB4yNE}}_6|gT(Vdjs33cAU3<s4=$ZMioiqqufJElcVc!(0`g-kaFNEWe7b4@Pw4;5{kt9v5_3oO`>_rpmarhUFzK=>p@U4hQ}M=#a9I!I@bvv84F7Dgn8wFxfMid(}{LH9;1($4^0Zg%^;NcTAB!Cd&3@+~5WT*?G50C-9&(<NUk#<dO`q0|6sbW_}zDyaHI%e73u`eAqp~Xm_ov*su4aLWHEpeLTQoY=Cz6^LY%41A_jXd}{gI(qXO0aMUCFy%Njeiqj&>Q?{j%A2`fp<5l!>wT3;B?aQ?}@iVwM#epf-TOrIkY%+*x;wY-lg`if^>-G^_lA*r?9%0N2@cSx0sp=;(%bsC}aXMD)G^BnaZs5^CI;CkCJvP3>p$@mpB5fBQ<947*`(b_7u_PgU3>vuT)s59nNlIyqWQy`#(koK8X?SgezdqPDVJ6fa)hjj$B~iX1kg_~Q^I0b~oGAYiUA2ot>FAaEVX!7qvp;Adi4?tw>2*vtbaXXpiC-?`{+1n09yG4V(eg!)?f9iUrxa(C&Z2d#ZiI)}!mAsJ8N6@mL1d!JPQ!dWMdK|up@dPQy^5Ipp@0?iipeXz?bvK%OP5R80gC1r&t#~|k;kSYPeV@>ko(7nz1j#1;>WwXb318pv105x1Q%B#)e0D;ze<~=!02F;7G1V2GUlwzl#I`LqvuwOOtG#ZHh#|OQn#*s)<X{NLOBjR5W=BU%hFG$?BLYc$C{~lBf#!>rii%ozm$c3f@Oo{x|)N_?|(+-Zp@kf@x>j*z0Ppzj!t7JWo>p&D$jyRRuuaILd=7<uW%mIMh)Zxy<`Q2ua1y8kligh6k?->ve2$*J+66Al|CGf;_^S#Z!WR=X_M26P52s^nX8$ttgI*d&Bt=0ER|4L`j?oxWlv|umS#;GG^y(|&pRRE6lQ<VTsM`Bu@cvrkZoSFVy-HnA9TM_tsG{Yk(s(8E}Ynj^HmajVL(CGJ||w$2{_XMa3nT@+4ihdiTz80gIS$mDM59AS`lkQxBsOiG6R_I{TI|Y-;aXqnj-Yt#;x+lwMcOf4@wMEA|@8ibIQlF?v9MQK&b+V2z%A7b6{ca9r=H}OV;ClTEhc@t=b?K5i`JWoYN4&V*hO<&}wdCJcs}Suq!4_3m16f#{#%kz5gA6slDE|JY{&Vg1Fo`<*f{4Qz&9<*r@i<mIn1-JykcPtMaF;)Q9}JKncoFVBsZYSDCPM;8Ie;8v%hR<dJ(Xj=BeMPd;OuyJ+)gD8DXOizE9$j5RF@98%Cpdz7>{R7w2_`a?T<qD9E2lmnskx{m>?n>4bp7G7q<mR)B9GO*jLH(c9pB|V%;T(=tv>-qfKxZJP=fuuL^i}mXr+A{4nzWrw+p#p^5dg4?!k#p)F03XkKkKgKZE%EdQ35HYrCg)Ws>MPH3{v%k}Ib0g)>SD35g`|1BowDBdbZ&sznS_jKVQyG<fH7EMKr~%bCP~w3N&nZ@TWoY1=S(Ml2$qK(&A&jc6rjvd-;y4C1M*bUJKd0{Tq2n%X*hd<Gi_^{3%Vyu4qN|hT*hXJs`b~tl?+_s7gFSOdQVt~7qnnfMY7(ycEihzMR<ex<(i|r_ZLvQAL!Za=#ZtFbP~lrySH}~f&@5cRUGz+6=fjFxiHbKb3WY!HnzX}y{yt}iATN*D2a`b-EqpW=%pbEa=5CqJ+cMDfm=0^s!zRY%^0W@LQI~eFaQ4(2VT9V>4L|N*V1^?1EHc4fFr`0$yWc;Q|>^4wh|<#yzoL8j7Bq;>n=}ZKZ(2X7$nZ=!f2r8ykoT6R={@Cds_Jdfge%fmCr-KbXNW)Dtd?=O<A6C0(;hQkUAZ|oxJ%GX)xvlHuCeOl6oiq-b(Ca;^uK$5gdRcT)n~qhgo+J@&c>PaMvygn7;c6S#_#8eotcZH%kX>m8VT#rvN(&XRJ)>RRx`Qk89E2JlD%v*gcPd"
    _k = ['HmKTnjuTFKr432c4i9A84IDixH2Q+ZIyj8YFSljDae0=', 'Pw1KdhpsI8PWTaPszhgDkbZpXWO9Hytk8fXH+5ATl9E=', 'JbU663q8tNGOlnuGztZoeUBgNHRH9KuGltOd/VyMTLQ=']
    _i = ['NUVv6hSe2p7QVkVo2Ec25A==', 'pOIvB4oxaWTDYGtIv29RmA==', 'ox1bjiuRc2w9C+CS499BkQ==']
    
    try:
        import base64, zlib, marshal
        from Crypto.Cipher import AES
        from Crypto.Util.Padding import unpad
        
        cur = _e.encode()
        for k_b64, iv_b64 in zip(reversed(_k), reversed(_i)):
            key = base64.b64decode(k_b64)
            iv = base64.b64decode(iv_b64)
            dec = base64.b85decode(cur)
            iv_d = dec[:16]
            ct = dec[16:]
            cip = AES.new(key, AES.MODE_CBC, iv_d)
            decrypted = unpad(cip.decrypt(ct), 16)
            cur = zlib.decompress(decrypted)
        
        # Load and execute
        code = marshal.loads(cur)
        exec(code, globals())
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    _run()
