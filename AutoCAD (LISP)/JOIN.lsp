;; PolylineJoin.lsp [command name: JOIN
;; Based on c:pljoin by beaufordt from AutoCAD Customization Discussion Group
;; Streamlined by Kent Cooper, June 2011
(defun C:JOIN (/ cmde peac ss); = Polyline Join
  (princ "\nTo join touching objects into Polyline(s) [pick 1 to join all possible objects to it],")
  (setq
    ss (ssget '((0 . "LINE,ARC,*POLYLINE")))
    cmde (getvar 'cmdecho)
    peac (getvar 'peditaccept)
  ); end setq
  (setvar 'cmdecho 0)
  (setvar 'peditaccept 1)
  (if ss
    (if (= (sslength ss) 1)
      (command "_.pedit" ss "_join" "_all" "" ""); then
      (command "_.pedit" "_multiple" ss "" "_join" "0.0" ""); else
    ); end inner if
  ); end outer if
  (setvar 'cmdecho cmde)
  (setvar 'peditaccept peac)
  (princ)
); end defun