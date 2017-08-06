#!/usr/bin/perl
#
# Usage: 
# 
#   correlation.pl GS system
#
#      FIXES BUG IN FIRST RELEASE
# 
#   Note: the GS file and system files need to have the same number of
#         lines
#



use Getopt::Long qw(:config auto_help); 
use Pod::Usage; 
use warnings;
use strict;
use Statistics::Basic qw(correlation) ;
use Statistics::RankCorrelation;

my $gs ;
my $sys ;
my $DEBUG = '' ;

GetOptions("debug" => \$DEBUG) 
    or
    pod2usage() ;

pod2usage if $#ARGV != 1 ;

# load GS results
open(I,$ARGV[0]) or die $! ;
while (<I>) {
    chomp ;
    my ($g) = split(/\t/, $_);
    push @$gs, $g ;
} 
close(I) ;
printf "GS:  %d scores\n",scalar(@$gs)   if  $DEBUG ;

# load system results
# takes number in first field, 
# discards rest of fields
open(I,$ARGV[1]) or die $! ;
while (<I>) {
    chomp ;
    my ($score) = split(/\t/,$_) ;
    warn "$ARGV[1]: score is not between 0 and 5" if (($score<0) or ($score>5)) and $DEBUG ;
    push @$sys, $score;
} 
close(I) ;
printf "SYS: %d scores\n",scalar(@$sys)  if  $DEBUG ;


# Compute Pearson
printf "Pearson: %.5f\n",correlation($gs,$sys) ;


# compute Spearman
my $c = Statistics::RankCorrelation->new($gs, $sys);
printf "Spearman: %.5f\n", $c->spearman;
printf "Kendall: %.5f\n", $c->kendall;
