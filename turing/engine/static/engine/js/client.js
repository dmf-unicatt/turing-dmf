function bestCopy(src) {
    return Object.assign({}, src);
}

function increaseSlider(slider, step) {
    slider.triggerHandler('input');
    slider[0].stepUp();
}

class Gara {
    constructor(data) {
        // Costruisce la gara a partire dai dati forniti dal server
        console.log("start building Gara");

        this.inizio = new Date(data.inizio);
        if (data.inizio == null) {
            this.inizio = null;
            this._time = null;
        }

        this.n_prob = data.n_prob;
        this.fixed_bonus = data.fixed_bonus;
        this.super_mega_bonus = data.super_mega_bonus;
        this.n_blocco = data.n_blocco;
        this.k_blocco = data.k_blocco;
        this.cutoff = data.cutoff;
        this.jolly_enabled = data.jolly_enabled;

        this.problemi = {};
        for (var i in data.problemi)
            this.problemi[i] = new Problema(this, i, data.problemi[i]["nome"], data.problemi[i]["punteggio"]);

        this.squadre = {}
        for (var i in data.squadre)
            this.squadre[i] = new Squadra(this, i, data.squadre[i]["nome"], data.squadre[i]["ospite"]);

        if (data.inizio == null) return;

        this.last_update = new Date(data.last_update);
        this.last_event = 0;
        this._time = this.inizio; // Parte a calcolare dall'inizio della gara
        this.fine = new Date(data.fine);
        this.en_plein = 0;

        for (var i in data.jolly) {
            // Imposta quali risposte valgono doppio
            this.add_jolly(data.jolly[i])
        }

        this.futuro = [];
        for (var i in data.consegne) {
            this.add_event(data.consegne[i]);
        }

        this.passato = [];

        console.log(this);
    }

    add_jolly(event) {
        var sq_idx = event.squadra
        var prob = event.problema
        this.squadre[sq_idx].jolly = this.squadre[sq_idx].risposte[prob];
        this.squadre[sq_idx].jolly.is_jolly = true;
        this.last_event = event.id
    }

    add_event(event) {
        this.futuro.push(new Evento(this, event));
        this.last_event = event.id;
    }

    get time() {
        return this._time
    }

    set time(value) {
        // Si sposta al tempo specificato, calcolando gli eventi in mezzo
        if (value >= this.time) {
            // Stiamo andando in avanti
            while (this.futuro.length > 0 && this.futuro[0].orario <= value) {
                // Processa eventi, finché il prossimo evento non è troppo avanti
                var e = this.futuro[0];
                this._time = e.orario // Porta la gara all'ora della consegna


                if (e.pts_prec == null) {
                    // Se non era già stato fatto, calcola la posizione attuale e il punteggio
                    e.pts_prec = e.squadra.punteggio;
                    e.pos_prec = e.squadra.posizione(this.classifica);
                }

                e.squadra.risposte[e.problema.id].consegna(e.giusta);

                if (e.pts_succ == null) {
                    e.pts_succ = e.squadra.punteggio;
                    e.pos_succ = e.squadra.posizione(this.classifica);
                }
                this.passato.push(e);
                this.futuro.shift();
            }
        }
        else {
            // Stiamo tornando indietro
            while (this.passato.length > 0 && this.passato[this.passato.length-1].orario > value) {
                var e = this.passato[this.passato.length-1];
                this._time = e.orario // Porta la gara all'ora della consegna

                e.squadra.risposte[e.problema.id].undo_consegna(e.giusta);

                this.passato.pop();
                this.futuro.unshift(e);
            }
        }
        // Finalmente, setta il tempo della gara
        this._time = value;
    }

    get progess() {
        return (this.time - this.inizio)/(this.fine-this.inizio)
    }

    set progress(value) {
        if (this.inizio == null) return;
        // Si sposta al progress specificato, calcolando gli eventi in mezzo
        if (value==null)
            this.time = Date.now();
        else
            this.time = new Date(this.inizio.getTime()+Math.floor((this.fine-this.inizio)*value));
    }

    get soglia_blocco() {
        // Il momento in cui i problemi smettono di salire
        if (this.inizio == null) return new Date();
        return new Date(this.fine.getTime() - 1000*60*20);
    }

    get scadenza_jolly() {
        // Il momento dopo il quale mostrare i jolly
        if (this.inizio == null) return new Date();
        return new Date(this.inizio.getTime() + 1000*60*10);
    }

    get en_plein_bonus() {
        return this.super_mega_bonus[this.en_plein] || 0;
    }

    custom_sort(a, b) {
        // sort by points
        if (a.pts < b.pts) return 1
        if (a.pts > b.pts) return -1;

        // sort by jolly
        if (a.squadra.jolly != null && b.squadra.jolly != null) {
            var jolly_diff = b.squadra.jolly.punteggio - a.squadra.jolly.punteggio;
            if (jolly_diff != 0) return jolly_diff;
        }

        // sort by
        var pba = Object.entries(a.squadra.risposte).map(x => x[1].punteggio).sort().reverse();
        var pbb = Object.entries(b.squadra.risposte).map(x => x[1].punteggio).sort().reverse();
        if (pba<pbb) return 1;
        if (pba>pbb) return -1;

        // TODO: sort by timestamp
        return 0;

    }

    get classifica() {
        console.log("classifica");
        var ret = [];
        for (var i in this.squadre) {
            ret.push({
                squadra: this.squadre[i],
                pts: this.squadre[i].punteggio
            })
        }
        // Ordina secondo il regolamento
        ret.sort(this.custom_sort)
        return ret
    }

    get punti_problemi() {
      var ret = [];
      for (var i in this.problemi) {
          ret.push({
              id: this.problemi[i].id,
              base: this.problemi[i].punti_base,
              bonus: this.problemi[i].bonus
          })
      }
      return ret
    }

}

class Problema {
    // Descrive lo stato di un problema
    constructor(gara, id, nome, punteggio) {
        this.id = id;
        this.gara = gara;
        this.nome = nome;
        this.punteggio = punteggio;
        this.lock_time = (gara.n_blocco == 0) ? gara.inizio : null; // Tempo a cui il problema si è bloccato
        this._risposte_corrette = 0; // Contatore del numero di risposte corrette
        this._risposte_sbagliate = 0; // Contatore delle risposte sbagliate prima della prima soluzione
    }

    // Segnala al problema una nuova risposta, per adeguare il suo valore
    // NON deve essere chiamata dalla risposta di una squadra ospite
    aggiungi_risposta(giusta) {
        if (giusta) {
            this._risposte_corrette += 1;
            if (this._risposte_corrette == this.gara.n_blocco && this.gara.time <= this.gara.soglia_blocco) {
                this.lock_time = this.gara.time
            }
        }
        else {
            if (this._risposte_corrette == 0 && this.gara.time <= this.gara.soglia_blocco) {
                this._risposte_sbagliate += 1;
            }
        }
    }

    rimuovi_risposta(giusta) {
        // Annulla l'effetto di aggiungi_risposta
        if (giusta) {
            this._risposte_corrette -= 1;
            if (this._risposte_corrette == this.gara.n_blocco - 1 && this.gara.time <= this.gara.soglia_blocco) {
                this.lock_time = null;
            }
        }
        else {
            if (this._risposte_corrette == 0 && this.gara.time <= this.gara.soglia_blocco) {
                this._risposte_sbagliate -= 1;
            }
        }
    }

    get bloccato() {
        return this.lock_time != null || this.gara.time > this.gara.soglia_blocco
    }

    get punti_base() {
        // Restituisce il valore base del problema
        if (this.lock_time != null)
            var t = this.lock_time;
        else if (this.gara.time > this.gara.soglia_blocco)
            var t = this.gara.soglia_blocco;
        else
            var t = this.gara.time;

        var derivata = Math.floor((t - this.gara.inizio) / 60000);
        var bonus_errori = this._risposte_sbagliate * 2;
        return this.punteggio + derivata + bonus_errori;
    }

    get bonus() {
        // Restituisce il bonus corrente
        return this.gara.fixed_bonus[this._risposte_corrette] || 0;
    }
}

class Risposta {
    // Descrive lo stato di un problema per una squadra, e contiene il punteggio ottenuto in quel problema
    constructor(squadra, problema) {
        this.squadra = squadra;
        this.gara = squadra.gara;
        this.problema = problema;
        this.risolto = 0;
        this.errori = 0;
        this._is_jolly = false
        this._bonus = 0;
    }

    get is_jolly() {
        if (!this.gara.jolly_enabled) return false;

        if (this.gara.time < this.gara.scadenza_jolly)
            return false;
        else if (this.squadra.jolly == null)
            return this.problema.id == 1;
        else
            return this._is_jolly
    }

    set is_jolly(value) {
        this._is_jolly = value
    }

    consegna(giusta) {
        if (giusta) {
            this.risolto += 1;
            if (this.risolto == 1) {
                this._bonus = this.problema.bonus;
                this.squadra.aggiungi_risposta(true);
                if (!this.squadra.ospite)
                    this.problema.aggiungi_risposta(true);
            }
        }
        else {
            if (this.risolto>=1) return;
            this.errori += 1;
            this.squadra.aggiungi_risposta(false);
            if (!this.squadra.ospite && (this.gara.k_blocco == null || this.errori <= this.gara.k_blocco))
                //Dice al problema che c'è un errore solo se non supera k.
                this.problema.aggiungi_risposta(false);
        }
    }

    undo_consegna(giusta) {
        // Annulla una consegna al tempo corrente
        if (giusta) {
            this.risolto -= 1;
            if (this.risolto == 0) {
                this._bonus = this.problema.bonus;
                this.squadra.rimuovi_risposta(true);
                if (!this.squadra.ospite)
                    this.problema.rimuovi_risposta(true);
            }
        }
        else {
            if (this.risolto>=1) return;
            this.errori -= 1;
            this.squadra.rimuovi_risposta(false);
            if (!this.squadra.ospite && (this.gara.k_blocco == null || this.errori < this.gara.k_blocco))
                this.problema.rimuovi_risposta(false);
        }
    }

    get punteggio() {
        var pts = 0;
        if (this.risolto) {
            pts += this.problema.punti_base + this._bonus;
        }

        pts -= this.errori * 10;

        if (this.is_jolly)
            pts = pts * 2;

        return pts
    }
}

class Squadra {
    constructor(gara, id, nome, ospite=false) {
        this.id = parseInt(id);
        this.nome = nome;
        this.gara = gara;
        this.ospite = ospite;
        this.jolly = null // Indica il problema jolly scelto dalla squadra
        this.risposte = {}
        for(var i in this.gara.problemi) {
            this.risposte[i] = new Risposta(this, this.gara.problemi[i])
        }
        this._risposte_corrette = 0;
        this._en_plein_bonus = 0;
    }

    aggiungi_risposta(giusta) {
        // Dice alla squadra che è stata data una nuova risposta, per calcolare i bonus en plein
        if (giusta) {
            this._risposte_corrette += 1;
            if (this._risposte_corrette == this.gara.n_prob) {
                this._en_plein_bonus = this.gara.en_plein_bonus;
                if (!this.ospite)
                    // Se la squadra non è ospite, shifta l'array dei bonus en plein
                    this.gara.en_plein += 1;
            }
        }
    }

    rimuovi_risposta(giusta) {
        // Annulla l'effetto di aggiungi_risposta
        if (giusta) {
            this._risposte_corrette -= 1;
            if (this._risposte_corrette == this.gara.n_prob - 1) {
                this._en_plein_bonus = 0;
                if (!this.ospite)
                    // Se la squadra non è ospite, shifta l'array dei bonus en plein
                    this.gara.en_plein -= 1;
            }
        }
    }

    get punteggio() {
        // Calcola il punteggio della squadra
        var pts = this.gara.n_prob * 10;
        pts += this._en_plein_bonus;
        for(var i in this.risposte) {
            pts += this.risposte[i].punteggio
        }
        return pts
    }

    posizione(classifica) {
        var pos = 1;
        for(var i=0; classifica[i].squadra!=this; i++) {
            if (!classifica[i].squadra.ospite) {
                pos += 1;
            }
        }
        return pos
    }
}

class Evento {
    // Descrive una consegna, e contiene le informazioni necessarie per generare un commento
    constructor(gara, data) {
        this.gara = gara;
        if (data.orario > gara.fine)
            // Se l'evento è avvenuto dopo la fine, fallo accadere alla fine.
            this.orario = new Date(gara.fine);
        else
            this.orario = new Date(data.orario);
        this.squadra = gara.squadre[data.squadra];
        this.problema = gara.problemi[data.problema];
        this.giusta = data.giusta;
        this.pos_prec = null;
        this.pos_succ = null;
        this.pts_prec = null;
        this.pts_succ = null;
    }

    get frase() {
        // jolly risolto
        if (this.giusta && this.squadra.risposte[this.problema.id].is_jolly) {
          if (this.pos_succ != this.pos_prec){
            return `La squadra ${this.squadra.nome} risolve il proprio jolly, guadagnando ${this.pts_succ-this.pts_prec} punti e salendo in posizione ${this.pos_succ}`;
          }
          else{
            return `La squadra ${this.squadra.nome} risolve il proprio jolly, guadagnando ${this.pts_succ-this.pts_prec} punti, ma rimanendo in posizione ${this.pos_succ}`;
          }
        }

        // alta classifica
        if (this.pos_succ<5) {
            if (this.pts_prec<this.pts_succ)
              if (this.pos_succ != this.pos_prec)
                return `La squadra ${this.squadra.nome} risolve il problema ${this.problema.id} e sale in posizione ${this.pos_succ}`;
              else
                return `La squadra ${this.squadra.nome} risolve il problema ${this.problema.id}, ma rimane in posizione ${this.pos_succ}`;
            else
              if (this.pos_succ != this.pos_prec)
                return `La squadra ${this.squadra.nome} sbaglia il problema ${this.problema.id} e scende in posizione ${this.pos_succ}`;
              else
                return `La squadra ${this.squadra.nome} sbaglia il problema ${this.problema.id}, ma rimane in posizione ${this.pos_succ}`;
        }

        // molti punti?
        if (this.pts_succ-this.pts_prec>99)
          if (this.pos_succ != this.pos_prec)
            return `La squadra ${this.squadra.nome} risolve il problema ${this.problema.id}, guadagnando ${this.pts_succ-this.pts_prec} punti e salendo in posizione ${this.pos_succ}`;
          else
            return `La squadra ${this.squadra.nome} risolve il problema ${this.problema.id}, guadagnando ${this.pts_succ-this.pts_prec} punti, ma rimanendo in posizione ${this.pos_succ}`;

        // se non succede niente di interessante ritorna null
        return null;
    }

}

class ClassificaClient {
    constructor(url, view, following=[]) {
        this.url = url;
        this.view = view;
        this.following = following;
        this.autoplay = 0;
        this.recalculating = false;
    }

    init() {
        console.log("client init");
        var self = this;
        $.getJSON(this.url).done(function(data){
            self.recalculating = true;
            self.gara = new Gara(data);
            self.following = data.consegnatore_per
            self.progress = null;
            self.recalculating = false;
        });
    }

    update(progress=null) {
        var self = this;
        if (this.recalculating) return;
        if (this.gara.inizio == null) {
            this.init();
            return
        }
        var last_event_before = this.gara.last_event;
        $.getJSON(this.url, {last_event: last_event_before}).done(function(data){
            var new_lu = new Date(data.last_update);
            if (new_lu > self.gara.last_update) {
                // C'è stata una modifica grossa, serve un ricalcolo totale
                self.init();
                return;
            }
            // Evitiamo di riconteggiare alcuni eventi già arrivati; succede se la rete sta laggando
            if (self.gara.last_event > last_event_before) return;

            // Aggiungiamo le nuove consegne e jolly
            for (var i in data.consegne) {
                self.gara.add_event(data.consegne[i]);
            }
            for (var i in data.jolly) {
                self.gara.add_jolly(data.jolly[i])
            }
            self.progress = progress;
        });
    }

    get progress() {
        return this.gara.progress;
    }

    set progress(value) {
        // Porta la gara al punto specificato, e aggiorna l'HTML
        this.gara.progress = value;
        this._aggiornaHTML();
    }

    _aggiornaHTML() {
        this._stampaOrologio();
        switch (this.view) {
            case 'squadre': this._mostraClassifica(); break;
            case 'problemi': this._mostraPuntiProblemi(); break;
            case 'stato': this._mostraStatoProblemi(); break;
            case 'cronaca': this._mostraCronaca(); break;
            case 'unica': this._mostraUnica(); break;
        }
        document.dispatchEvent(new Event('updated'));
    }

    _stampaOrologio() {
        if (this.gara.inizio!=null) {
            var fine = new Date(this.gara.fine);
            var t_mancante = Math.max(fine - this.gara.time, 0); // Se la gara è finita, restituisce 0
            var res = new Date(t_mancante).toISOString().substr(11, 8);
            $("#orologio").text(res);
        }
    }

    _mostraClassifica() {
        var classifica = this.gara.classifica
        var max = classifica.length > 0 ? classifica[0].pts : 0;
        max = Math.max(max,this.gara.n_prob*10*4);

        var sq, pts;
        for (var i in classifica) {
            var sq = classifica[i].squadra;
            var pts = classifica[i].pts;
            var pos = sq.posizione(classifica);
            var elapsed = (this.gara.time - this.gara.inizio)/1000;
            if (this.gara.cutoff != null && this.gara.cutoff >= pos && !sq.ospite && elapsed >= 60*20)
                $("#team-"+sq.id).addClass("cutoff");
            else $("#team-"+sq.id).removeClass("cutoff");
            $("#team-"+sq.id).css('width', Math.round(pts/max*1000)/10+'%');
            $("#label-pos-"+sq.id).text(pos+"°");
            $("#label-points-"+sq.id).text(pts);
            $("#label-points-mobile-"+sq.id).text(pts);
        }

        for (const sq_id of this.following) {
            $("#team-"+sq_id).addClass("following");
        }

        // if (this.cutoff == null) {
        //     $("#cutoff").addClass('d-none');
        // }
        // else {
        //     var bRect = $("#team-"+cutoff_team.id)[0].getBoundingClientRect();
        //     var pos = $("#classifica-container")[0].getBoundingClientRect();
        //     $("#cutoff").css('left', (bRect.right-pos.left-1)+'px');
        // }
        // Spara un evento per comunicare che la pagina si è aggiornata
    }

    _mostraPuntiProblemi() {
        var punti_problemi = this.gara.punti_problemi
        var max = Math.max(...punti_problemi.map((x) => x.base + x.bonus), 80) // Restituisce il max tra 80 e le somme tra base e bonus
        for (var k in punti_problemi) {
            var id = punti_problemi[k].id
            $("#label-"+id).text((id)+" - "+this.gara.problemi[id].nome);
            $("#punti-"+id).css('width', Math.round(punti_problemi[k].base*100./max)+'%');
            $("#label-punti-"+id).text(punti_problemi[k].base);
            if (this.gara.problemi[id].bloccato)
                $("#punti-"+id).removeClass("progress-bar-striped progress-bar-animated");
            else
                $("#punti-"+id).addClass("progress-bar-striped progress-bar-animated");
            $("#bonus-"+id).css('width', Math.round(punti_problemi[k].bonus*100./max)+'%');
            if (punti_problemi[k].bonus) $("#label-bonus-"+id).text(punti_problemi[k].bonus);
            $("#label-punti-mobile-"+id).text(punti_problemi[k].base+" + "+punti_problemi[k].bonus);
        }
    }

    _mostraStatoProblemi() {
        for (var i in this.gara.squadre) {
            var sq = this.gara.squadre[i];
            for (var j in sq.risposte) {
                var r = sq.risposte[j];
                var text = "";
                $("#cell-"+i+"-"+j).removeClass("wrong-answer right-answer")

                if (r.risolto) {
                    $("#cell-"+i+"-"+j).addClass("right-answer");
                }
                else if (r.errori) {
                    $("#cell-"+i+"-"+j).addClass("wrong-answer");
                    text += '<b>'+r.errori+'</b>'
                }

                if (r.is_jolly) {
                    text += ClassificaClient.stella_jolly;
                    //text0 = '<i class="fas fa-star float-right"></i>';
                }

                $("#cell-"+i+"-"+j).html(text);
            }
        }

        for (const sq_id of this.following) {
            $("#riga-"+sq_id).addClass("following");
        }
    }

    _mostraCronaca() {
        var classifica = this.gara.classifica
        var max = classifica.length > 0 ? classifica[0].pts : 0;
        max = Math.max(max,this.gara.n_prob*10*4);

        for (const sq_id of this.following) {
            $("#team-"+sq_id).addClass("following");
        }

        for (var i in classifica) {
            var sq = classifica[i].squadra
            $("#team-"+sq.id).css('width', Math.round(classifica[i].pts/max*1000)/10+'%');
            $("#label-"+sq.id).text(sq.posizione(classifica) + "° - " + sq.nome);
            $("#label-points-"+sq.id).text(classifica[i].pts);
        }

        var h = $("#div-1").outerHeight();
        var options = {"duration": 800, "queue": false};
        if (this.autoplay) options = {"duration": 100, "queue": false, "easing": "linear"};
        for (i=0; i<classifica.length; i++) {
            var sq = classifica[i].squadra;
            var dist = h*(i+1-sq.id);
            $("#div-"+sq.id).animate({
                top: dist
            }, options);
        }

        if (this.gara.inizio != null) {
            $("#frasi").empty();
            $("#frasi").prepend('<li class="list-group-item">Gara iniziata!</li>');
            for (var e in this.gara.passato) {
                var f = this.gara.passato[e].frase;
                if (f!=null) $("#frasi").prepend('<li class="list-group-item">'+f+'</li>');
            }
        }

    }

    _mostraUnica() {
      var classifica = this.gara.classifica
      var punti_problemi = this.gara.punti_problemi
      for (var i in punti_problemi){
          var text = ""
          var problema = (parseInt(i)+1)
          text+="#"+("0"+problema).slice(-2)+"\n"+punti_problemi[i].base+"+"+punti_problemi[i].bonus
          $("#pr-"+problema).html(text)
      }
      for (var i in classifica) {
          var sq = classifica[i].squadra;
          var riga = parseInt(i)+1;
          if (sq.ospite) $("#riga-"+riga).addClass("text-muted");
          else $("#riga-"+riga).removeClass("text-muted");
          $("#pos-"+riga).html(sq.posizione(classifica)+"° ");
          $("#nome-"+riga).html(sq.nome);
          $("#punt-"+riga).html(""+sq.punteggio);
          for (var j in sq.risposte) {
              var r = sq.risposte[j];
              var text = "";
              $("#cell-"+riga+"-"+j).removeClass("wrong-answer right-answer")

              if (r.risolto) {
                  $("#cell-"+riga+"-"+j).addClass("right-answer");
              }
              else if (r.errori) {
                  $("#cell-"+riga+"-"+j).addClass("wrong-answer");
              }
              if(r.risolto || r.errori)
                text += '<span><b>'+r.punteggio+'</b></span>'

              if (r.is_jolly) {
                  text += ClassificaClient.stella_jolly;
              }

              $("#cell-"+riga+"-"+j).html(text);
          }

          if (this.following.includes(sq.id)) $("#riga-"+riga).addClass("following");
          else $("#riga-"+riga).removeClass("following");
      }
    }

    toggleReplay(button, slider_id) {
        this.autoplay = 1 - this.autoplay;
        console.log(this.autoplay ? 'Autoplay started' : 'Autoplay stopped');
        if (this.autoplay) {
            button.innerHTML = '<i class="fas fa-pause"></i>';
            var slider = $("#"+slider_id);
            if (slider[0].value == 1000) slider[0].value = 0;
            increaseSlider(slider, 1);
            this.autoplayInterval = setInterval(increaseSlider, 100, slider, 1);
        }
        else {
            button.innerHTML = '<i class="fas fa-play"></i>';
            clearInterval(this.autoplayInterval);
        }
    }
}

ClassificaClient.stella_jolly = `<span class="my-fa-stack">
    <i class="fas fa-star fa-stack-1x fa-inverse" style="color:yellow"></i>
    <i class="far fa-star fa-stack-1x" style="color:black"></i>
</span>`;
