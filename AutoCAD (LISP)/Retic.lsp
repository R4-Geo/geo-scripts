;******************************************************************************
;* COMANDO RETIC                                                              *
;* Dibuja un reticulado en el layer RETIC con lineas horizontales y su        *
;* coordenada Norte, y lineas verticales con su cordenada Este. Por cada linea*
;* se crean dos textos iguales de cordenada, uno en cada punta.               *
;* El reticulado es dibujado dentro una zona rectangular cuyos extremos son   *
;* pedidos al usu rio.                                                        *
;* El reticulado es dibujado en el UCS actual.                              *
;* Dados de Entrada:                                                          *
;*            Distancia horizontal entre lineas                               *
;*            Distancia vertical entre lineas                                 *
;*            Altura de los textos                                            *
;*            Precision, o numero de casas decimales de las coordenadas       *
;*            Canto Superior Izquierdo y                                      *
;*            Canto Inferior Derecho de la zona rectangular a reticular       *
;*                                                                            *
;* Se puede hacer Undo despues de dibujar el reticulado, para borrarlo.       *
;* Si las lineas cortan textos de las coordenadas perpendiculares,            *
;* vuelva a hacer el reticulado en una zona un poco mas grande.               *
;* Es conveniente dibujar un borde antes del reticulado, para usar sus        *
;* cantos como referencia.                                                    *
;*                                                                            *
;*         Desarrollado en 29/05/96 Por Paulo Borralho, GEOSYS                *
;*                                                                            *
;******************************************************************************


(defun c:RETIC ( / #wid #hi p1 p2 xi yi n ptsup ptinf ptesq ptdta berror s)
    (defun berror (msg)(setq *error* m:err m:err nil)(princ))
    (setq m:err *error* *error* berror)
    (setq #wid (ureal 7 "" "Intervalo Horizontal" nil);espa‡amento horizontal
          #hi (if #wid (ureal 7 "" "Intervalo Vertical" #wid)) ;espa‡amento vertical
          #htxt (if #hi (ureal 7 "" "Altura de Texto" nil)) ;h texto
          #prec (if #hi (uint 5 "" "Precision" 0));          precisao

    )
    (princ "Inserte Margenes")
    (if (and #wid #hi
             (setq p1 (getpoint "\nEsquina Superior Izquierdo:"))
        )
       (setq p2 (getcorner p1 "\nEsquina Inferior Derecho:"))
    )
    (if (and p1 p2)
        (progn
            (mlayer "RETIC" nil nil T)   ;se n„o existe cria layer RETIC

            ;------------TXT X------------------------------
            (setq xi (* #wid (fix (/ (+ (* 2 #htxt)(car p1)) #wid))))
            (if (< xi (+ (car p1) (* 2 #htxt))) (setq xi (+ #wid xi)))
            (setq n (fix (/ (- (car p2) xi) #wid)))
            (repeat (1+ n)
                 ;TEXTO X ACIMA
                 (setq ptsup (trans (list xi (cadr p1) 0) 1 0)
                       ptinf (trans (list xi (cadr p2) 0) 1 0)
                       ang (angle ptinf ptsup)
                 )
                 (setq s (strcat " E-" (rtos xi 2 #prec) " "))
                 (entmake  (list '(0 . "TEXT")             ;tipo de entidd
                      '(8 . "RETIC")               ;no layer RETIC
                      (cons 1 s)                   ;texto
                      (cons 40  #htxt)                  ;altura
                      (cons 50 ang)          ;angulo em rad 90§
                      '(72 . 2)                    ;just Horizontal centrar 1
                      '(73 . 1)                    ;just Vertical
                      (cons 10 ptsup)
                      (cons 11 ptsup)
                 )        )
                 ;TEXTO X ABAIXO
                 (entmake  (list '(0 . "TEXT")             ;tipo de entidd
                     '(8 . "RETIC")               ;no layer RETIC
                      (cons 1 s)                   ;texto
                      (cons 40  #htxt)                  ;altura
                       (cons 50 ang)          ;angulo em rad 90§
                      '(72 . 0)                    ;just Horizontal centrar 1
                      '(73 . 1)                    ;just Vertical
                      (cons 10 ptinf)
                      (cons 11 ptinf)
                 )        )
                 (entmake (list '(0 . "LINE")
                     '(8 . "RETIC")               ;no layer RETIC
                     (cons 10 ptsup) (cons 11 ptinf)        ;desenha a linha
                    '(210 0 0 1)
                 )   )
                 (setq xi (+ #wid xi))
            );repeat n+1
            ;------------TXT Y------------------------------

            (setq yi (* #hi (fix (/ (- (cadr p1) (* 2 #htxt)) #hi))))
            (if (>  yi (- (cadr p1)(* 2 #htxt))) (setq yi (- yi #hi)))
            (setq n (fix (/ (- yi (cadr p2)) #hi)))
            (repeat (1+ n)
                 ;TEXTO Y ESQ
                 (setq ptesq (trans (list (car p1) yi 0) 1 0)
                       ptdta (trans (list (car p2) yi 0) 1 0)
                       ang   (angle ptesq ptdta)
                 )
                 (setq s (strcat " N-" (rtos yi 2 #prec) " "))
                 (entmake  (list '(0 . "TEXT")             ;tipo de entidd
                     '(8 . "RETIC")               ;no layer RETIC
                      (cons 1 s)                   ;texto
                      (cons 40  #htxt)                  ;altura
                      (cons 50 ang)          ;angulo em rad 90§
                      '(72 . 0)                    ;just Horizontal   dta
                      '(73 . 1)                    ;just Vertical acima
                      (cons 10 ptesq)
                      (cons 11 ptesq)
                 )        )
                 ;TEXTO Y DTA
                 (entmake  (list '(0 . "TEXT")             ;tipo de entidd
                     '(8 . "RETIC")               ;no layer RETIC
                      (cons 1 s)                   ;texto
                      (cons 40  #htxt)             ;altura
                      (cons 50  ang)                    ;angulo em rad 0§
                      '(72 . 2)                    ;just Horizontal   esq
                      '(73 . 1)                    ;just Vertical  acima
                      (cons 10 ptdta)
                      (cons 11 ptdta)
                 )        )
                 ;LINHA HORIZONTAL
                 (entmake (list '(0 . "LINE")
                    '(8 . "RETIC")               ;no layer RETIC
                     (cons 10 ptesq) (cons 11 ptdta)        ;desenha a linha
                    '(210 0 0 1)
                 )   )
                 (setq yi (- yi #hi))             ;para linha acima
            );repeat n+1
        );progn
    );if
);defun txttram

;-----------------------------------------------------------------------
;* Ureal: User Interface Real Function
;* BIT 0 for none, and KWD key word ("" for none) are same as for initget
;* MSG is the prompt string, to which a default real is added as <DEF>
;* (nil for none), and a : is added
;-----------------------------------------------------------------------
(defun ureal (bit kwd msg def / inp)
  (if def
     (setq msg (strcat "\n" msg "<" (rtos def) ">: " )
           bit (* 2 (fix (/ bit 2)))
     );setq
     (if (= " " (substr msg (strlen msg) 1))
        (setq msg (strcat "\n" (substr msg 1 (1- (strlen msg))) ": "))
        (setq msg (strcat "\n" msg ": "))
  )  );ifif
  (initget bit kwd)
  (setq inp (getreal msg))
  (if inp inp def)
);ureal
;-----------------------------------------------------------------------
;* Uint: User Interface Integer Function
;* BIT 0 for none, and KWD key word ("" for none) are same as for initget
;* MSG is the prompt string, to which a default integer is added as <DEF>
;* (nil for none), and a : is added
;-----------------------------------------------------------------------
(defun uint (bit kwd msg def / inp)
  (if def
     (setq msg (strcat "\n" msg "<" (itoa def) ">: " )
           bit (* 2 (fix (/ bit 2)))
     );setq
     (if (= " " (substr msg (strlen msg) 1))
        (setq msg (strcat "\n" (substr msg 1 (1- (strlen msg))) ": "))
        (setq msg (strcat "\n" msg ": "))
  )  );ifif
  (initget bit kwd)
  (setq inp (getint msg))
  (if inp inp def)
);uint


;*--------------------------------------------------------------------------
;* MLAYER : modificar layer com COR LTYPE THAW .confirma existencia.
;*          Se n„o existe cria-o. Argumentos nil n„o se tomam em conta
;*--------------------------------------------------------------------------
(defun MLAYER (nome cor ltype thaw / reg)
    (setq reg (getvar "REGENMODE"))
    ;guarda var sis. e muda-a a 0 p/ (em caso de erro ‚ reposta)
    ; se n„o est  a fun‡„o tempor usa setvar
    (if tempor (tempor "REGENMODE" 0)(setvar "REGENMODE" 0))
    (if (tblsearch "LAYER" nome)
        (command "LAYER" )             ;j  existe, chama-se cmd Layer
        (command "LAYER" "N" nome)     ;faz Novo, nao existia
    )
    (if cor (command "c" cor nome))
    (if ltype (command "LT" nome))
    (if thaw (command "T" nome "")
             (command "F" nome "")
    )
    (setvar "REGENMODE" reg)
)

