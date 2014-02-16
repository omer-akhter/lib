// ==UserScript==
// @name        page-mods
// @namespace   http://iynaan.com/page-mods
// @include     *
// @version     1
// @grant       none
// @require     http://ajax.googleapis.com/ajax/libs/mootools/1.4.5/mootools-yui-compressed.js
// ==/UserScript==

window.addEvent( 'domready', function() {
  if ( window.__pagemods__ ) {
    return;
  }

  var PageMod = new Class( {
    Implements : [ Options ],
    options : {
      utubeframehide : false
    },

    initialize : function( options ) {
      this.setOptions( options );
      this.isFrame = ( window.frameElement ? true : false );
    },

    initStyles : function() {
      var styles = '.utubediv {\n';
      styles += '\tborder : medium solid gray;\n';
      styles += '\tmargin : 3px;\n';
      styles += '\tpadding : 5px;\n';
      styles += '\tborder-radius: 5px;\n}\n';

      styles += '.utubetoggle { /*width: 0.8em, height: 0.8em,*/\n';
      styles += '\tborder : thin solid black;\n';
      styles += '\tbackground : white;\n';
      styles += '\tcolor : gray;\n';
      styles += '\tpadding : 1px 2px 1px 3px;\n';
      styles += '\tmargin : 2px 2px 2px 10px;\n';
      styles += '\tborder-radius: 7px;\n';
      styles += '\width: 8px;\n';
      styles += '\tfloat : right;\n';
      styles += '\tcursor: pointer;\n';
      styles += '\tfont-size : 8px;\n}\n';

      new Element( 'style', {
        text : styles
      } ).inject( document.body );
    },

    handleUtubeFrame : function( frameEle, index, frameEleList ) {
      frameEle = document.id( frameEle );
      var url = frameEle.get( 'src' );
      //console.log( 'iframe.src:', url );

      if ( !/youtube\.com\/embed/.test( url ) ) {
        return;
      }

      var utubeFrame = new UtubeDiv( {}, frameEle ).create();
    },

    handleUtubeFrames : function() {
      var frameEleList = $$( 'iframe' );
      //var frameEleList = document.getElementsByTagName( 'iframe' );
      console.log( 'frames:', frameEleList.length );

      Array.each( frameEleList, this.handleUtubeFrame, this );
    },

    run : function() {
      this.initStyles();
      this.handleUtubeFrames();
    }
  } );

  var UtubeDiv = new Class( {
    Implements : [ Options ],
    options : {
      framestyles : {
        border : 'medium dashed blue',
        opacity : '0.2'
      }
    },

    initialize : function( options, frameEle ) {
      this.setOptions( options );
      this.frameEle = document.id( frameEle );
      // console.log( 'frameEle:', frameEle );
    },

    create : function() {
      var url = this.frameEle.get( 'src' );
      this.divEle = new Element( 'div', {
        'class' : '__pagemods __utubediv utubediv'
      } ).wraps( this.frameEle );

      var toggleFn = this.toggle.bind( this );
      this.toggleEle = new Element( 'span', {
        text : '+',
        'class' : 'utubetoggle',
        events : {
          click : toggleFn
        }
      } ).inject( this.divEle, 'top' );

      /*this.linkEle = */new Element( 'a', {
        href : url,
        text : url
      } ).inject( this.divEle, 'top' );

      this.divEle.store( 'utubediv', this );
      this.divEle.setStyle( 'width', this.frameEle.getStyle( 'width' ) );

      this.heightOriginal = this.frameEle.getStyle( 'height' );
      this.frameEle.removeProperty( 'height' );
      this.frameEle.get( 'tween' ).addEvent( 'complete', function( frameEle ) {
        var height = frameEle.getStyle( 'height' ).toInt();
        if ( height === 0 ) {
          frameEle.setStyle( 'display', 'none' );
        }
      } );
      this.frameEle.tween( 'height', 0 );

      try {
        this.frameEle.contentWindow.stop();
      }
      catch ( e ) {
        console.log( 'could not stop frame loading:', e );
      }

      return this;
    },

    toggle : function( event ) {
      event.stop();
      var height = this.frameEle.getStyle( 'height' ).toInt();
      if ( height === 0 ) {
        this.frameEle.setStyle( 'display' );
        this.frameEle.tween( 'height', this.heightOriginal );
        this.toggleEle.set( 'html', '&#8212;' );
      }
      else {
        this.frameEle.tween( 'height', 0 );
        this.toggleEle.set( 'text', '+' );
      }
    }
  } );

  console.log( '### page-mods ###:', window.location.href );
  window.__pagemods__ = new PageMod();
  window.__pagemods__.run();
} );
