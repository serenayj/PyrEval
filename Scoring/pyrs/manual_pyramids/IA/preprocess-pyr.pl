#!/usr/bin/perl
## Input: two *pyr files created using DUCView
## Output: a table that can be the input to reliTools/multi-reli-missing-new.pl
## Creation Date: 29 Feb 2016
## Author: Becky Passonneau        


use strict;
use warnings;
use autodie;

use List::MoreUtils qw(uniq);

die "\nUsage: preprocess-pyr.pl <FILE1> <FILES2> <ANN1> <ANN2>\n\n\twhere <FILE1> and <FILE2> are two *pyr files from DucView, <ANN1> and <ANN2> are the names of the annotators.\n\tOutput is input for interannotator agreement.\n" unless (@ARGV==4);

my $first = $ARGV[0];
my $second = $ARGV[1];
my $ann1 = $ARGV[2];
my $ann2 = $ARGV[3];
my $pyr1 = 1;
my $pyr2 = 2;
my @infiles = ($first,$second);
my @pyramids;              ## pyramid numbers
my %summaries;             ## $summaries{$pyramid} = $text
my %pyramidsin;            ## $pyramidsin{$pyramid} = $xmltext
my %xmlcheck;              ## $xmlcheck{$pyramid}{$start}{$end}
my @pyramidwords;          ## stores all the words from the pyramid source texts
my %pyramidwords;          ## sequential ids for all the source text words
my %rpyramidwords;         ## reverse index for %pyramidwords
my %contributorwords;      ## $contributorwords{$start}{$end}{$scu}{$pyramid} = $word
my $warning;               ## print if xml does not check out
my %scus;                  ## $scus{$pyr}{$scu}="id1==word1,id2==word2,...,idn==wordn"
my %fortable;              ## $fortable{$wordid}{$pyr}=$list-of-scu-wordids==words

## read in each pyramid's set of summaries into %summaries
## and read the pyramid xml into %pyramidsin
my $pyramidnum;
foreach my $in (@infiles) {
    $pyramidnum++;
    push @pyramids, $pyramidnum;
    my $status=0;
    open(my $pyr, "<", $in);
    while(<$pyr>) {
	if(m/<line>([^<]+)<\/line>/){
	    my $text = $1;
	    if ($text =~ /\w+ \w+ \w+/) {
#		print "NEXT TEXT: $text\n";
		$summaries{$pyramidnum} .= " $text" if $summaries{$pyramidnum};
		$summaries{$pyramidnum} = $text unless $summaries{$pyramidnum};
	    }
	}
	## save xml into %pyramidsin
	## save all contributor start/end pairs into %xmlcheck
	elsif($status==1) {
	    $pyramidsin{$pyramidnum} .= $_ if $pyramidsin{$pyramidnum};
	    $pyramidsin{$pyramidnum} = $_ unless $pyramidsin{$pyramidnum};
	    if(m/start=\"([0-9]*)\" end=\"([0-9]*)\"/){
	        my $start=$1;
		my $end=$2;
		$xmlcheck{$pyramidnum}{$start}{$end}=1;
	    }
	}
	elsif(m/<\/text>/) { $status = 1; }
    }
    close($pyr);
}

## confirm the two sets of summaries have been read in
my $pyramid1=0;
my $pyramid2=0;
foreach my $pyramid (sort numeric keys %summaries) {
#    print "\nSUMMARY SET $pyramid\n";
#    print "==$summaries{$pyramid}==\n";
    if(!$pyramid1) {
	$pyramid1 = $summaries{$pyramid};
    }
    if(!$pyramid2) {
	$pyramid2 = $summaries{$pyramid};
    }
}
## STEP 1: confirm the two sets of summaries are identical
my $do=0;
my $finalword;
if ($pyramid1 eq $pyramid2) {
    print "SUMMARIES OF THE TWO PYRAMIDS MATCH\n";
    $do=1;
    $pyramid1 = &splitcontractions($pyramid1);
    $pyramid1 = &splithyphenated($pyramid1);
    @pyramidwords = split /\s+/, $pyramid1;
}
else {
    print "PROBLEM: SUMMARIES OF THE TWO PYRAMIDS DO NOT MATCH\n";
}

## STEP 2: verify the xml does not have overlapping contributors
print "\nVERIFYING XML\n";
foreach my $pyr (sort numeric keys %xmlcheck) {
    my $lastend=0;
    foreach my $start (sort numeric keys %{$xmlcheck{$pyr}}) {
#	print "\nPYRAMID $pyr NEXT START $start ";
	foreach my $end (sort numeric keys %{$xmlcheck{$pyr}{$start}}) {
#	    print "NEXT END $end\n";
	    if ($lastend >= $start) {
		$do=0;
#		print "\n  LASTEND $lastend GEQ START $start\n";
		$warning="  OVERLAPPING CONTRIBUTOR IN PYRAMID $pyr AT $start, $end.\nFIX PYRAMID.\n\n";
		print $warning;
		$lastend=$end;
	    }
	    else {
#		print "\n  LASTEND $lastend NOTGEQ START $start\n";
#		print "VERIFIED PYRAMID $pyr $start $end\n";
		$lastend=$end;
	    }
	}
    }
}
print "\nDONE WITH VERIFICATION\n";
if ($do) {
    print "STARTING ANALYSIS\n";
    my $wordid=0;

    ## index all the words by sequential ids
#    print "\nALL WORDS IN SUMMARIES\n";
    foreach my $word (@pyramidwords) {
	$wordid++;
	$word=&cleanup($word);
#	print "$wordid\t$word\n";  #test pyramids: word 1 "Matter" to word 1336 "shape"
	$pyramidwords{$wordid}=$word;
	$rpyramidwords{$word}=$wordid;
    }

    ## STEP 3: For each pyramid, identify each word by start and end char positions, and by scu
    foreach my $pyramid (sort numeric keys %pyramidsin) {
	my $scu=0;
	my $contributor=0;
#	print "\nPYRAMID $pyramid\n";
#	print "$pyramidsin{$pyramid}\n";
	my @pyramid = split /\n/, $pyramidsin{$pyramid};
	foreach my $element (@pyramid) {
#	    print "\nIN $element\n";
	    if($element =~ /<scu uid=\"([^\"]*)\"/) {
		$scu = $1;
		$contributor=0;
#		print "\nSCU: $scu\n";
	    }
	    elsif($element =~ /<part label="([^\"]*)" start="([^\"]*)" end="([^\"]*)"/) {
		my $text = $1;
		my $start = $2;
		my $end = $3;
		$contributor++;
#		print "\nSCU $scu CONTRIBUTOR $contributor, START $start, END $end, TEXT $text\n";
		&wordpositions($start,$end,$text,$scu,$pyramid);
	    }
	}
    }

    ## Print %contributorwords to verify STEP 2 
    foreach my $pyramid (sort numeric keys %contributorwords) {
#    	print "\n";
    	foreach my $start (sort numeric keys %{$contributorwords{$pyramid}}) {
    	    foreach my $end (sort numeric keys %{$contributorwords{$pyramid}{$start}}) {
    		foreach my $scu (sort numeric keys %{$contributorwords{$pyramid}{$start}{$end}}) {
#    		    print "PYR $pyramid, START $start END $end SCU $scu:";
#    		    print " $contributorwords{$pyramid}{$start}{$end}{$scu}\n";
    		}
    	    }
    	}
    }

    ## STEP 4: GET WORDIDS FOR EACH CONTRIBUTORWORD AND ADD TO SCU FOR A GIVEN PYRAMID
    ## $fortable{$wordid}{$pyr}=$scuwordids
    my $sumword = "==";
    foreach my $pyr (sort numeric keys %contributorwords) {
#	print "\n";
    	my $counter;
    	foreach my $start (sort numeric keys %{$contributorwords{$pyr}}) {
    	    foreach my $end (sort numeric keys %{$contributorwords{$pyr}{$start}}) {
    		foreach my $scu (sort numeric keys %{$contributorwords{$pyr}{$start}{$end}}) {
    		    my $pyrword = $contributorwords{$pyr}{$start}{$end}{$scu};
		    do {
			$counter++;
			$sumword = $pyramidwords{$counter};
#			print "\n$counter PYR $pyr PYRWORD $pyrword SUMWORD $sumword\n";
		    } while ($pyrword ne $sumword);
		    $scus{$pyr}{$scu} .= ",$counter==$pyrword" if $scus{$pyr}{$scu};
		    $scus{$pyr}{$scu} = "$counter==$pyrword" unless $scus{$pyr}{$scu};
    		}
    	    }
    	}
    }

#    print "\nSCUs FOR EACH PYRAMID\n";
    foreach my $pyr (sort numeric keys %scus) {
#	print "PYRAMID $pyr\n";
	foreach my $scu (sort numeric keys %{$scus{$pyr}}) {
#	    print "$scus{$pyr}{$scu}\n";
	    my @scu = split /\,/, $scus{$pyr}{$scu};
	    foreach my $contrib (@scu) {
		my($wordid,$word) = split /==/, $contrib;
		$fortable{$wordid}{$pyr} = $scus{$pyr}{$scu};
	    }
	}
    }

    foreach my $wordid (sort numeric keys %pyramidwords) {
	foreach my $pyr (@pyramids) {
    	    $fortable{$wordid}{$pyr} = "NULL" unless $fortable{$wordid}{$pyr};
#    	    print "PYR $pyr WORDID $wordid $fortable{$wordid}{$pyr}\n" if $fortable{$wordid}{$pyr} eq "NULL";
 	}
    }

    

    # print "\nLEXICAL VERSION OF TABLE\n";
    # foreach my $word (sort numeric keys %fortable) {
    # 	print "$word";
    # 	foreach my $pyr (sort numeric keys %{$fortable{$word}}) {
    # 	    my $value = $fortable{$word}{$pyr};
    # 	    $value =~ s/^[0-9]*==//;
    # 	    $value =~ s/\,[0-9]*==/\&\&/g;
    # 	    print "\t$value";
    # 	}
    # 	print "\n";
    # }

    print "\nNUMERIC VERSION OF TABLE\n";
    foreach my $word (sort numeric keys %fortable) {
	print "$word";
	foreach my $pyr (sort numeric keys %{$fortable{$word}}) {
	    my $value = $fortable{$word}{$pyr};
	    $value =~ s/==[^0-9]*\,/\&\&/g;
	    $value =~ s/==[^0-9]*$//g;
	    print "\t$value" if $value =~ /\d/;
	    print "\tNULL" unless $value =~ /\d/;
	}
	print "\n";
    }

}

else {
    print "CANNOT CREATE TABLE DUE TO ",$warning;
}

sub numeric ($$) {
    my($a,$b) = @_;
    $a <=> $b
}

## input:  a contributor phrase, and start/end positions
## output: start/end of each word in the contributor phrase stored in 
##         $contributorwords{$pyramid}{$start}{$end}{$scu} = $word
## 1. check that the start/end is correct
## 2. split text on single space into an array
## 3. foreach $word in array, start is prev actual end + 1
##      new actual end is start + length($word)
##      if &splitcontractions || &splithyphenated || &cleanup then new virtual end
##         is start + length(cleanedup($word))
sub wordpositions {
    my($start,$end,$text,$scu,$pyramid)=@_;
    $text = &splitcontractions($text);
    $text = &splithyphenated($text);
    my $textlength = length($text);
#    print "\nWORDPOSITIONS IN PYR $pyramid: $text\nFROM $start TO $end (length $textlength)\n";
    my @words = split /\s+/, $text;
    my $actualend = $end;
    my $virtualend = 0;
#    print "\nTEST:"; for (@words) {print " $_ ";} print "\n";
    for (my $i=0; $i<=$#words; $i++) {
	my $word = $words[$i];
	my $origlength = length($word);
	$actualend = $start + $origlength;
#	print "\nFIND NEXT WORD: =$word= \n  IN $text AT $start\n";
	my $newword = &cleanup($word);
	my $newlength = length($newword);
	## &cleanup() removes chars, so the actual original end
	## will be greater than the new virtual end
	$virtualend = $start + $newlength;
#	print "  START POSITION: $start\n  END POSITION: $virtualend FOR $word (NOW $newword)\n";
	$contributorwords{$pyramid}{$start}{$virtualend}{$scu}=$newword if $newword =~ /\w/;
	$start = $actualend + 1;
    }
}

## removes one single quote char, adds one space char;
## length unchanged
sub splitcontractions {
    my($text) = @_;
    $text =~ s/n\'t/n t/g;
    $text =~ s/([a-z])\'s/$1 s/g;
    return $text;
}

## removes one hyphen char, adds one space char;
## length unchanged
sub splithyphenated {
    my($text) = @_;
    $text =~ s/([a-z])\-([a-z])/$1 $2/g;
    return $text;
}

## removes chars
sub cleanup {
    my($word)=@_;
    $word =~ s/[\,\.\?\!\;\:]*$//g;
    $word =~ s/\?//g;
    $word =~ s/\://g;
    $word =~ s/\,//g;
    $word =~ s/\'//g unless $word =~ /(n\'t|[a-z]\'s)/;
    return $word;
}
